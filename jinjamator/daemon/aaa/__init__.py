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

import ldap3


from jinjamator.task.configuration import TaskConfiguration
# from jinjamator.plugin_loader.content import ContentPluginLoader
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
import json

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
            self._id_token = deepcopy(self._access_token["userinfo"])
            del self._access_token["userinfo"]

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


class LDAPAuthProvider(AuthProviderBase):
    def __init__(self, app=None):
        super(LDAPAuthProvider, self).__init__(app)
        self._name = "ldap"
        self._type = "ldap"
        self._display_name = "LDAP Login"
        self._server = None
        self._connection = None
        self._configuration = {}
        self._maximum_group_recursion = 5

    def register(self, **kwargs):
        """
        Register extension arguments
        """
        self._name = kwargs.get("name")
        self._configuration = kwargs
        self._maximum_group_recursion = int(
            self._configuration.get("maximum_group_recursion", 5)
        )

    def _resolve_groups_recursive(self, groups, current_level=0):
        """
        Recursively resolve LDAP group membership
        """

        retval = []
        current_level += 1
        if current_level >= self._maximum_group_recursion:
            log.error(
                f"Maximum recursion for _resolve_groups_recursive {current_level} reached"
            )
            return groups
        for group in groups:
            log.debug(f"resolve LDAP group: working on group {group}")
            retval += [group]
            obj_group = ldap3.ObjectDef("group", self._connection)
            results = ldap3.Reader(self._connection, obj_group, group).search()

            for result in results:

                retval += self._resolve_groups_recursive(
                    result["memberOf"], current_level
                )

        return retval

    def login(self, request):
        try:
            username = request.json.get("username")
            password = request.json.get("password")
        except Exception as e:
            username = request.args.get("username")
            password = request.args.get("password")
        if not username or not password:
            return {"message": "Invalid Request (did you send your data as json?)"}, 400

        for server_obj in self._configuration.get("servers", []):
            try:
                self._server = ldap3.Server(
                    server_obj.get("name", "<not configured>"),
                    get_info=ldap3.ALL,
                    port=server_obj.get("port", 636),
                    use_ssl=server_obj.get("ssl", True),
                )
                self._connection = ldap3.Connection(
                    self._server,
                    user=f"{self._configuration.get('domain','not_configured')}\\{username}",
                    password=password,
                    authentication="NTLM",
                    auto_bind=True,
                )

            except ldap3.core.exceptions.LDAPSocketOpenError as e:
                log.error(
                    f"Connection Error: {server_obj.get('name ','<not configured>')} not reachable"
                )
                continue

            except ldap3.core.exceptions.LDAPBindError as e:
                log.error(
                    f"Authentication Error: invalid username and or password for user {username}"
                )
                return {"message": "Invalid Credentials"}, 401

            if not self._connection:
                return {"message": "Authentication Backend not ready"}, 401

            obj_person = ldap3.ObjectDef("person", self._connection)
            obj_person += self._configuration.get("username_attr", "samAccountName")

            result = ldap3.Reader(
                self._connection,
                obj_person,
                self._configuration.get("user_base_dn"),
                f"samAccountName:={username}",
            ).search()

            if len(result) == 0:
                return {"message": "Invalid user_base_dn."}, 401
            if len(result) > 1:
                return {"message": "Ambiguous result from authentication backend"}, 401

            # log.debug('got result from LDAP: ', str(result))
            if self._configuration.get("resolve_groups_recursive"):
                resolved_user_groups = []
                resolved_user_groups += self._resolve_groups_recursive(
                    list(result[0]["memberOf"])
                )

            else:
                resolved_user_groups = result[0]["memberOf"]
            log.info(
                f"{username} effective group memberships:\n  "
                + "\n  ".join(resolved_user_groups)
            )
            for allowed_group in self._configuration.get("allowed_groups"):
                if allowed_group in resolved_user_groups:
                    # user is authenticated and allowed to login
                    user = User.query.filter_by(username=username).first()
                    if user is None:
                        self._log.info(
                            f"username {username} not found in local database -> creating"
                        )
                        user = User(username=username)
                        user.name = username

                    else:
                        self._log.info(f"username {username} found in local database")
                    user.aaa_provider = self._name
                    user.password_hash = user.hash_password(
                        "".join(
                            random.SystemRandom().choice(
                                string.ascii_letters + string.digits
                            )
                            for _ in range(128)
                        )
                    )  # generate max len random secure password on each login

                    # check_group_mapping
                    if self._configuration.get("map_groups"):
                        user.roles = []
                    for ad_group, mappings in self._configuration.get(
                        "map_groups", []
                    ).items():

                        for jm_group in mappings:
                            if ad_group in resolved_user_groups:

                                role = (
                                    db.session.query(JinjamatorRole)
                                    .filter_by(name=jm_group)
                                    .first()
                                )
                                if role:
                                    user.roles.append(role)
                                else:
                                    log.error(f"role {jm_group} not found")

                    db.session.add(user)
                    db.session.commit()
                    user = User.query.filter_by(username=username).first()

                    token = {}
                    token["access_token"] = (
                        "Bearer " + user.generate_auth_token().access_token
                    )
                    return token
                else:
                    log.debug(f"User {username} not in group {allowed_group}")
        return {"message": "Invalid Credentials"}, 401


def initialize(aaa_providers, _configuration):
    # plugin_loader = ContentPluginLoader(None)
    # for content_plugin_dir in _configuration.get(
    #     "global_content_plugins_base_dirs", []
    # ):
    #     plugin_loader.load(f"{content_plugin_dir}")

    for aaa_config_directory in _configuration.get("aaa_configuration_base_dirs", []):
        for config_file in sorted(glob(os.path.join(aaa_config_directory, "*.yaml"))):
            log.info(f"found aaa configuration {config_file}")
            cur_cfg = TaskConfiguration()
            # cur_cfg._plugin_loader = plugin_loader
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

            elif cur_cfg.get("type") == "ldap":
                prov_name = cur_cfg.get("name")
                aaa_providers[prov_name] = LDAPAuthProvider()
                aaa_providers[prov_name].register(
                    **deepcopy(cur_cfg.get("ldap_configuration", {}))
                )

            if cur_cfg.get("display_name"):
                aaa_providers[prov_name]._display_name = cur_cfg.get("display_name")
            if cur_cfg.get("name"):
                aaa_providers[prov_name]._name = cur_cfg.get("name")


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
