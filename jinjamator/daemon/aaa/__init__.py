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

from jinjamator.daemon.app import app
from jinjamator.daemon.database import db


from jinjamator.task.configuration import TaskConfiguration
from jinjamator.plugin_loader.content import ContentPluginLoader

from jinjamator.daemon.aaa.models import (
    User,
    Oauth2UpstreamToken,
    JinjamatorToken,
    JinjamatorRole,
)

from .methods.ldap import LDAPAuthProvider
from .methods.authlib import AuthLibAuthProvider
from .methods.local import LocalAuthProvider



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

import string

import logging
log = logging.getLogger()


aaa_providers = {}

from sqlalchemy import or_, and_


def initialize(aaa_providers, _configuration):
    plugin_loader = ContentPluginLoader(None)
    for content_plugin_dir in _configuration.get(
        "global_content_plugins_base_dirs", []
    ):
        plugin_loader.load(f"{content_plugin_dir}")

    for aaa_config_directory in _configuration.get("aaa_configuration_base_dirs", []):
        for config_file in sorted(glob(os.path.join(aaa_config_directory, "*.yaml"))):
            log.info(f"found aaa configuration {config_file}")
            cur_cfg = TaskConfiguration()
            cur_cfg._plugin_loader = plugin_loader
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
