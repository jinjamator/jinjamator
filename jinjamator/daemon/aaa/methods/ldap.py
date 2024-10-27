try:
    import ctypes
    ctypes.CDLL("libssl.so").OSSL_PROVIDER_load(None, b"legacy")
    ctypes.CDLL("libssl.so").OSSL_PROVIDER_load(None, b"default")
    import hashlib
except:
    pass 

from . import AuthProviderBase
from jinjamator.daemon.aaa.models import (
    User,
    JinjamatorRole,
)
import ldap3
import logging
import random
import string

log = logging.getLogger()
from jinjamator.daemon.app import app
from jinjamator.daemon.database import db


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
            log.info(
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
            username = request.json.get("username","").lower()
            password = request.json.get("password")
        except Exception as e:
            username = request.args.get("username","").lower()
            password = request.args.get("password")
        if '\\' in username:
            username=username.split('\\')[-1]
        if "@" in username:
            username=username.split('@')[0]


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

            except Exception as e:
                log.error(e)
                return {"message": "Unexpected authentication error, please contact your jinjamator administrator"}, 500

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
                                if role and role not in user.roles:
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


