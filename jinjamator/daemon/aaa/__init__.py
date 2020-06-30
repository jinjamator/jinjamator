# Copyright 2019 Wilhelm Putz

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import g, url_for, abort
from authlib.integrations.flask_client import OAuth, OAuthError
from authlib.integrations.sqla_oauth2 import create_save_token_func


from jinjamator.task.configuration import TaskConfiguration
from jinjamator.plugin_loader.content import init_loader
from jinjamator.daemon.app import app
from jinjamator.daemon.aaa.models import (
    User,
    Oauth2UpstreamToken,
    JinjamatorToken,
    JinjamatorRole,
)
from jinjamator.daemon.database import db
from datetime import datetime
from calendar import timegm
from flask import request


from jwt import InvalidSignatureError, ExpiredSignatureError
from functools import wraps

import random
from pprint import pformat
from glob import glob
import os
from copy import deepcopy
import logging
import string

log = logging.getLogger()
aaa_providers = {}
_global_ldr = init_loader(None)
from sqlalchemy import or_, and_


class AuthProviderBase(object):
    def __init__(self, app=None):
        self._app = app
        self._log = logging.getLogger()
        self._user = None
        self._redirect_uri = None
        self.static_users = []
        self.static_roles = []

    def register(self, **kwargs):
        self._log.info("not implemented")

    def init_app(self, app):
        self._app = app

    def login(self, request):
        self._log.info("not implemented")

    def authorize(self, request):
        self._log.info("not implemented")

    @property
    def logged_in_user(self):
        return self._user.username

    def get_token(self):
        # generate_auth_token
        db_token = JinjamatorToken.query.filter_by(user_id=self._user.id).first()

        if db_token:
            if self._user.verify_auth_token(db_token.access_token):
                return db_token.access_token

        log.debug(f"generating new token for user_id: {self._user.id}")
        return self._user.generate_auth_token().access_token

    def create_static_users(self):
        with app.app_context():
            for static_user in self.static_users:
                try:

                    existing = (
                        db.session.query(User)
                        .filter_by(username=static_user["username"])
                        .first()
                    )
                    if existing:
                        self._log.info(f"User {static_user['username']} already exists")
                        # return True
                        del static_user["username"]
                        new_user = existing
                        new_user.password_hash = User.hash_password(
                            static_user["password"]
                        )
                        new_user.aaa_provider = self._name
                        new_user.name = str(static_user["name"])
                    else:
                        new_user = User(
                            username=static_user["username"],
                            name=static_user["name"],
                            password_hash=User.hash_password(static_user["password"]),
                            aaa_provider=self._name,
                        )
                except IndexError as e:
                    self._log.error(f"Cannot create static user {e}")
                    return False

                # delete all existing roles for
                new_user.roles = []

                for static_user_role in static_user.get("roles", []):
                    role = (
                        db.session.query(JinjamatorRole)
                        .filter_by(name=static_user_role)
                        .first()
                    )
                    new_user.roles.append(role)

                db.session.add(new_user)
                try:
                    db.session.commit()
                except Exception as e:
                    self._log.error(f"Cannot create static user {e}")
                    return False
                db.session.refresh(new_user)
                self._log.info(
                    f"Created static user {new_user.username} with id {new_user.id} "
                )

        return True

    def create_static_roles(self):
        with app.app_context():
            for static_role in self.static_roles:
                try:
                    existing = (
                        db.session.query(JinjamatorRole)
                        .filter_by(name=static_role["name"])
                        .first()
                    )
                    if existing:
                        self._log.info(f"Role {static_role['name']} already exists")
                        continue

                    new_role = JinjamatorRole(name=static_role["name"])
                except IndexError as e:
                    self._log.error(f"Cannot create static role {e}")
                    return False

                db.session.add(new_role)
                try:
                    db.session.commit()
                except Exception as e:
                    self._log.error(f"Cannot create static role {e}")
                    return False
                db.session.refresh(new_role)
                self._log.info(
                    f"Created static role {new_role.name} with id {new_role.id} "
                )
        return True


class LocalAuthProvider(AuthProviderBase):
    def __init__(self, app=None):
        super(LocalAuthProvider, self).__init__(app)
        self._name = "local"
        self._type = "local"
        self._display_name = "Local Login"

    def login(self, request):
        try:
            username = request.json.get("username")
            password = request.json.get("password")
        except Exception as e:
            username = request.args.get("username")
            password = request.args.get("password")
        if not username or not password:
            return {"message": "Invalid Request (did you send your data as json?)"}, 400

        self._user = self.verify_password(username, password)
        if self._user:
            token = self.get_token()
            db_token = JinjamatorToken.query.filter_by(user_id=self._user.id).first()
            token = db_token.to_dict()
            token["access_token"] = f"Bearer {token['access_token']}"
            return token

        return {"message": "Invalid Credentials"}, 401

    def verify_password(self, username, password):

        user = User.query.filter_by(username=username).first()
        if not user or not user.verify_password(password):
            return None
        return user


class AuthLibAuthProvider(AuthProviderBase):
    def __init__(self, app=None):
        super(AuthLibAuthProvider, self).__init__(app)
        if self._app:
            self._oauth = OAuth(self._app)
        else:
            self._oauth = OAuth()
        self._name = None
        self._provider = None
        self._type = "authlib"
        self._display_name = "Authlib Login"

    def init_app(self, app):
        """
        Init oauth instance within Flask
        """
        self._app = app
        self._oauth.init_app(app)

    def register(self, **kwargs):
        """
        Register openid connect provider
        """

        self._name = kwargs.get("name")

        self._oauth.register(**kwargs)

    def login(self, request):
        """
        Start openid connect login procedure
        """
        if self._redirect_uri:
            redirect_uri = self._redirect_uri
        else:
            redirect_uri = url_for("api.aaa_auth", _external=True)
            self._redirect_uri = redirect_uri

        self._log.debug(
            f"Start openid connect login procedure via oidc provider {self._name}"
        )
        self._provider = getattr(self._oauth, self._name)
        return self._provider.authorize_redirect(redirect_uri)

    def authorize(self, request):
        if self._provider:
            self._access_token = self._provider.authorize_access_token()
            self._id_token = self._provider.parse_id_token(self._access_token)
            self._log.debug(self._id_token)
            self._username = self._id_token.get(
                "preferred_username", self._id_token.get("name")
            )
            if not self._username:
                abort(500, "Did not get a username from token")
            user = User.query.filter_by(username=self._username).first()
            if user is None:
                self._log.info(
                    f"username {self._username} not found in local database -> creating"
                )
                user = User(username=self._username)
                user.name = self._id_token["name"]

            else:
                self._log.info(f"username {self._username} found in local database")
            user.aaa_provider = self._name
            user.password_hash = user.hash_password(
                "".join(
                    random.SystemRandom().choice(string.ascii_letters + string.digits)
                    for _ in range(128)
                )
            )  # generate max len random secure password on each login
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(username=self._username).first()

            upstream_token = Oauth2UpstreamToken(
                user_id=user.id, aaa_provider=self._name, **self._access_token
            )
            db.session.merge(upstream_token)
            db.session.commit()

            self._user = user

            return True
        else:
            self._log.warn(
                f"AAA provider {self._name} has not been initialized properly"
            )
        return False

    def get_token(self):
        now = timegm(datetime.utcnow().utctimetuple())
        db_token = JinjamatorToken.query.filter_by(user_id=self._user.id).first()

        if db_token:
            if self._user.verify_auth_token(db_token.access_token):
                return db_token.access_token
        upstream_token = Oauth2UpstreamToken.query.filter_by(
            user_id=self._user.id
        ).first()

        if upstream_token.expires_at < now:
            log.debug(
                f"upstream token {upstream_token.expires_at} for user {self._user.id} expired {now}, refusing to generate a new local one"
            )
            return False
        else:
            log.debug(
                f"upstream token ({upstream_token.expires_at}) for user {self._user.id} valid ({now}) ttl {upstream_token.expires_at - now}"
            )
        log.debug(f"generating new token for user_id: {self._user.id}")
        return self._user.generate_auth_token().access_token


def initialize(aaa_providers, _configuration):

    for content_plugin_dir in _configuration.get(
        "global_content_plugins_base_dirs", []
    ):
        _global_ldr.load(f"{content_plugin_dir}")

    for aaa_config_directory in _configuration.get("aaa_configuration_base_dirs", []):
        for config_file in glob(os.path.join(aaa_config_directory, "*.yaml")):
            cur_cfg = TaskConfiguration()
            cur_cfg.merge_yaml(config_file)
            prov_name = cur_cfg.get("authlib_configuration", {}).get("name")

            if cur_cfg.get("type") == "authlib":
                app.config[f"{prov_name.upper()}_CLIENT_ID"] = cur_cfg.get("client_id")
                app.config[f"{prov_name.upper()}_CLIENT_SECRET"] = cur_cfg.get(
                    "client_secret"
                )
                if prov_name not in aaa_providers:
                    aaa_providers[prov_name] = AuthLibAuthProvider()
                aaa_providers[prov_name].register(
                    **deepcopy(cur_cfg.get("authlib_configuration", {}))
                )
                aaa_providers[prov_name].init_app(app)

                if cur_cfg.get("redirect_uri"):
                    aaa_providers[prov_name]._redirect_uri = cur_cfg.get("redirect_uri")

            elif cur_cfg.get("type") == "local":
                prov_name = cur_cfg.get("name")
                aaa_providers[prov_name] = LocalAuthProvider()
                if cur_cfg.get("redirect_uri"):
                    aaa_providers[prov_name]._redirect_uri = cur_cfg.get(
                        "redirect_uri", []
                    )
                if cur_cfg.get("static_roles"):
                    aaa_providers[prov_name].static_roles = cur_cfg.get(
                        "static_roles", []
                    )
                    aaa_providers[prov_name].create_static_roles()

                if cur_cfg.get("static_users"):
                    aaa_providers[prov_name].static_users = cur_cfg.get("static_users")
                    aaa_providers[prov_name].create_static_users()
            if cur_cfg.get("display_name"):
                aaa_providers[prov_name]._display_name = cur_cfg.get("display_name")


def require_role(role=None, permit_self=False):
    def decorator(func):
        @wraps(func)
        def aaa_check_role(*args, **kwargs):
            token_type = None
            if request.headers.get("Authorization"):
                try:
                    token_type, auth_token = request.headers.get("Authorization").split(
                        " "
                    )
                except:
                    abort(400, "Invalid Authorization Header Format")
            elif request.args.get("access_token"):
                try:
                    auth_token = request.args.get("access_token")
                    token_type = "Bearer"
                except:
                    abort(400, "Invalid Authorization access_token Format")

            if token_type == "Bearer":
                token_data = User.verify_auth_token(auth_token)
                if token_data:
                    now = timegm(datetime.utcnow().utctimetuple())
                    log.info(f'Access granted for user_id {token_data["id"]}')
                    new_token = None
                    if (token_data["exp"] - now) < app.config[
                        "JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME"
                    ]:
                        log.info(
                            f"renewing token as lifetime less than {app.config['JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME']}s"
                        )
                        new_token = (
                            User.query.filter_by(id=token_data["id"])
                            .first()
                            .generate_auth_token()
                            .access_token
                        )
                    if permit_self:  # permit access for endpoint
                        user_id_or_name = kwargs.get(
                            "user_id_or_name", kwargs.get("user_id")
                        )
                        user = User.query.filter(
                            or_(
                                User.id == user_id_or_name,
                                User.username == user_id_or_name,
                            )
                        ).first()
                        if user:
                            if user.id == token_data["id"]:
                                log.debug(
                                    f"permit self set -> permitting access for user_id {user.id} user_name {user.name} on own record"
                                )
                                retval = func(*args, **kwargs)
                                if new_token:
                                    return (
                                        retval,
                                        200,
                                        {"Authorization": f"Bearer {new_token}"},
                                    )
                                return retval
                            else:
                                user = None
                    if isinstance(role, str):
                        log.debug(f"required role {role} or administrator")
                        user = User.query.filter(
                            and_(
                                User.id == token_data["id"],
                                or_(
                                    User.roles.any(
                                        JinjamatorRole.name == "administrator"
                                    ),
                                    User.roles.any(JinjamatorRole.name == role),
                                ),
                            )
                        ).first()
                    elif role is None:
                        log.debug(
                            f"just a valid authentication with no special role required"
                        )
                        user = User.query.filter_by(id=token_data["id"]).first()

                    else:
                        if hasattr(role, "__module__"):
                            if role.__module__ == "sqlalchemy.sql.elements":
                                log.debug(
                                    f"got sqlalchemy sql expression as role {role} or administrator"
                                )
                                user = User.query.filter(
                                    and_(
                                        User.id == token_data["id"],
                                        or_(
                                            User.roles.any(
                                                JinjamatorRole.name == "administrator"
                                            ),
                                            role,
                                        ),
                                    )
                                ).first()

                    if user:
                        g._user = user.to_dict()
                        retval = func(*args, **kwargs)
                        if new_token:
                            return (
                                retval,
                                200,
                                {"Authorization": f"Bearer {new_token}"},
                            )
                        return retval

                    abort(
                        403,
                        f"Elevated privileges required, user neither has role {role} nor administrator",
                    )
                else:
                    abort(401, "Token invalid, please reauthenticate")
            else:
                abort(400, "Invalid Authorization Header Token Type")

            abort(
                403,
                "Authorization required, no Authorization Data found (Header,POST,GET",
            )

        return aaa_check_role

    return decorator
