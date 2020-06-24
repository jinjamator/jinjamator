import logging

from flask import request, flash, url_for, g, Response
from flask import Flask, url_for, session, redirect

from flask_restx import Resource, abort
from jinjamator.daemon.aaa import aaa_providers, require_role
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.parsers import aaa_login_get
from jinjamator.daemon.api.serializers import (
    aaa_login_post,
    aaa_create_user,
    aaa_create_role,
    aaa_set_user_role,
    environments,
)
from jinjamator.daemon.aaa.models import User, JinjamatorRole, JinjamatorRole as r
from jinjamator.daemon.database import db

from flask import current_app as app
import glob
import os
import xxhash
from pprint import pformat
from datetime import datetime
from calendar import timegm
from sqlalchemy import or_, and_

log = logging.getLogger()

ns = api.namespace(
    "aaa",
    description="Operations related to jinjamator Authentication Authorization and Accounting",
)

current_provider = None


@ns.route("/login/<provider_name>")
@api.doc(
    params={
        "provider_name": {
            "description": "The name of the login provider",
            "enum": list(aaa_providers.keys()),
        }
    }
)
class Login(Resource):
    @api.response(404, "Unknown Login Provider <provider_name>")
    @api.response(200, "Success")
    @api.response(302, "Redirect to IDP")
    @api.expect(aaa_login_get)
    def get(self, provider_name="local"):
        """
        Login User via GET request.
        OIDC providers will redirect to the authentication portal of the IDp, local authentication will directly return A valid access token
        Won't work from swaggerui with most OIDC providers due CORS restrictions.
        For testing OIDC copy the url generated by swagger and c&p it to a new browser tab.
        """
        if provider_name in aaa_providers:
            response = aaa_providers[provider_name].login(request)
            return response
        abort(404, f"Unknown Login Provider {provider_name}")

    @api.expect(aaa_login_post)
    def post(self, provider_name="local"):
        """
        Login User via POST request. 
        OIDC providers will redirect to the authentication portal of the IDp, local authentication will directly return A valid access token
        """
        if provider_name in aaa_providers:
            return aaa_providers[provider_name].login(request)
        abort(400, f"Unknown Login Provider {provider_name}")


@ns.route("/logout")
@api.response(400, "Not logged in")
@api.response(200, "Success")
class Logout(Resource):
    def get(self):
        """
        Logout User and terminate all session information.
        """
        if current_provider:

            return {"message": "not implemented"}
        else:
            abort(400, "Not logged in")


@ns.route("/auth")
@api.response(401, "Upstream token expired, please reauthenticate")
@api.response(301, "Redirect to jinjamator web with access_token as GET parameter")
@api.response(400, "Cannot find valid login provider")
class Auth(Resource):
    def get(self):
        """
        Extract token from OIDC authentication flow and redirect to jinjamator web with access_token as GET parameter.
        This REST Endpoint should never be called directly.
        """
        for aaa_provider in aaa_providers:
            log.debug(f"trying to use {aaa_provider}")
            if aaa_providers[aaa_provider].authorize(request):
                current_provider = aaa_providers[aaa_provider]
                token = current_provider.get_token()
                if token:
                    url = url_for("webui.index", access_token=token, _external=True)
                    if request.headers:
                        proto = request.headers.get("X-Forwarded-Proto", "http")
                    else:
                        proto = "http"
                    url = url.replace("http", proto)
                    redir = redirect(url)
                    return redir
                else:
                    abort(401, "Upstream token expired, please reauthenticate")
        abort(400, "Cannot find valid login provider")


@ns.route("/token")
class VerifyToken(Resource):
    @api.doc(
        params={
            "Authorization": {"in": "header", "description": "A valid access token"}
        }
    )
    def get(self):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                token_type, auth_token = auth_header.split(" ")
            except:
                abort(400, "Invalid Authorization Header Format")
            if token_type == "Bearer":
                token_data = User.verify_auth_token(auth_token)
                if token_data:
                    now = timegm(datetime.utcnow().utctimetuple())
                    log.info((token_data["exp"] - now))
                    if (token_data["exp"] - now) < app.config[
                        "JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME"
                    ]:
                        log.info(
                            f"renewing token as lifetime less than {app.config['JINJAMATOR_AAA_TOKEN_AUTO_RENEW_TIME']}"
                        )
                        token = (
                            User.query.filter_by(id=token_data["id"])
                            .first()
                            .generate_auth_token()
                            .access_token
                        )
                        return (
                            {
                                "message": f'login ok user id {token_data["id"]}, you got a new token',
                                "status": "logged_in_new_token_issued",
                                "user_id": token_data["id"],
                                "token_ttl": token_data["exp"] - now,
                                "access_token": f"Bearer {token}",
                            },
                            200,
                            {"access_token": f"Bearer {token}"},
                        )

                    return {
                        "message": f'login ok user id {token_data["id"]}',
                        "status": "logged_in",
                        "user_id": token_data["id"],
                        "token_ttl": token_data["exp"] - now,
                        "auto_renew_in": token_data["exp"] - now - 300,
                    }

                else:
                    abort(400, "Token invalid, please reauthenticate")
            else:
                abort(400, "Invalid Authorization Header Token Type")
        else:
            abort(401, "Authorization required, no Authorization Header found")


@ns.route("/users")
@api.response(400, "Parameters missing, or not properly encoded")
@api.response(200, "Success")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class Users(Resource):
    @require_role(role="user_administration")
    def get(self):
        """
        List all registred users.
        """
        retval = []
        for user in User.query.all():
            retval.append(user.to_dict())
        return retval

    @api.expect(aaa_create_user)
    @require_role(role="user_administration")
    def post(self):
        """
        Create a new Jinjamator User.
        """
        try:
            new_user = User(
                username=request.json["username"],
                name=request.json["name"],
                password_hash=User.hash_password(request.json["password"]),
                aaa_provider=request.json.get("aaa_provider", "local"),
            )
        except IndexError:
            abort(400, "Parameters missing, or not properly encoded")
        db.session.add(new_user)
        try:
            db.session.commit()
            db.session.refresh(new_user)
            return new_user.to_dict()
        except:
            abort(400, "User exists")


@ns.route("/users/<user_id_or_name>")
@api.doc(
    params={
        "Authorization": {"in": "header", "description": "A valid access token"},
        "user_id_or_name": "The User ID of the user which should be returned",
    }
)
@api.doc(params={})
@api.response(404, "User ID not found")
@api.response(200, "Success")
class UserDetail(Resource):
    @require_role(role="user_administration", permit_self=True)
    def get(self, user_id_or_name):
        """
        Get details about an user.
        """
        user = User.query.filter(
            or_(User.id == user_id_or_name, User.username == user_id_or_name)
        ).first()
        if user:
            return user.to_dict()
        else:
            abort(404, "User ID not found")

    @require_role(role="user_administration", permit_self=True)
    def delete(self, user_id_or_name):
        """
        Delete an user.
        """
        try:
            if (
                User.query.filter(
                    or_(User.id == user_id_or_name, User.username == user_id_or_name)
                ).delete()
                == 1
            ):
                db.session.commit()
                return {"message": f"deleted user {user_id_or_name}"}

        except Exception as e:
            abort(500, f"Error, cannot remove user {user_id_or_name} : {e}")
        return {"message": f"user {user_id_or_name} not found"}, 404


@ns.route("/users/<user_id_or_name>/roles")
@api.doc(
    params={
        "Authorization": {"in": "header", "description": "A valid access token"},
        "user_id_or_name": "The User ID of the user which roles should be returned",
    }
)
@api.response(200, "Success")
class UserRolesDetail(Resource):
    @api.response(404, "User ID not found")
    @require_role(role="user_administration", permit_self=True)
    def get(self, user_id_or_name):
        """
        List roles attached to an user.
        """

        user = User.query.filter(
            or_(User.id == user_id_or_name, User.username == user_id_or_name)
        ).first()
        if user:
            return user.to_dict()["roles"]
        else:
            abort(404, "User ID not found")

    @api.response(404, "User ID not found")
    @api.expect(aaa_set_user_role)
    @require_role(role="user_administration")
    def post(self, user_id_or_name):
        """
        Add a role to an user.
        """
        user = User.query.filter(
            or_(User.id == user_id_or_name, User.username == user_id_or_name)
        ).first()

        if user:

            db_role = JinjamatorRole.query.filter_by(
                name=request.json.get("role")
            ).first()
            if db_role:
                user.roles.append(db_role)
                db.session.commit()
                db.session.refresh(user)

            return user.to_dict()["roles"]
        else:
            abort(404, "User ID not found")

    @api.response(404, "User has no role with specified name or user id not found")
    @api.expect(aaa_set_user_role)
    def delete(self, user_id_or_name):
        """
        Remove a role from an user.
        """
        user = User.query.filter(
            or_(User.id == user_id_or_name, User.username == user_id_or_name)
        ).first()
        role = request.json.get("role")
        if user:
            try:
                user.roles.remove(role)
                db.session.commit()
                db.session.refresh(user)
            except ValueError:
                abort(404, f"User has no role {role}")
            return user.to_dict()["roles"]
        else:
            abort(404, "User ID not found")


@ns.route("/roles")
@api.doc(
    params={"Authorization": {"in": "header", "description": "A valid access token"}}
)
class Roles(Resource):
    @api.response(200, "Success")
    @require_role(role="role_administration")
    def get(self):
        """
        List available user roles.
        """
        retval = []
        for role in JinjamatorRole.query.all():
            retval.append(role.to_dict())
        return retval

    @api.response(201, "Created Role")
    @api.response(400, "Invalid request")
    @api.expect(aaa_create_role)
    @require_role(role="role_administration")
    def post(self):
        """
        Create a new role.
        """
        try:
            new_role = JinjamatorRole(name=request.json["name"])
        except IndexError:
            abort(400, "Parameters missing, or not properly encoded")
        db.session.add(new_role)
        try:
            db.session.commit()
            db.session.refresh(new_role)
            return new_role.to_dict(), 201
        except:
            abort(400, "Role exists")


@ns.route("/roles/<role_id_or_name>")
@api.doc(
    params={
        "Authorization": {"in": "header", "description": "A valid access token"},
        "role_id_or_name": "The role ID or the role name of the role which should be returned",
    }
)
@api.response(200, "Success")
@api.response(404, "Role not found")
class RoleDetail(Resource):
    @require_role(role="role_administration")
    def get(self, role_id_or_name):
        """
        Get detailed information about a role.
        """
        role = JinjamatorRole.query.filter(
            or_(
                JinjamatorRole.id == role_id_or_name,
                JinjamatorRole.name == role_id_or_name,
            )
        ).first()
        if role:
            return role.to_dict()
        else:
            abort(404, f"JinjamatorRole id or name {role_id_or_name} not found")

    @require_role(role="role_administration")
    @api.response(204, "Role deleted")
    def delete(self, role_id_or_name):
        """
        Delete a role.
        """
        role = JinjamatorRole.query.filter(
            or_(
                JinjamatorRole.id == role_id_or_name,
                JinjamatorRole.name == role_id_or_name,
            )
        ).first()
        if role:
            db.session.delete(role)
            db.session.commit()
            return {"message": f"successfully deleted role {role_id_or_name}"}, 204
        else:
            abort(404, f"JinjamatorRole id or name {role_id_or_name} not found")


@ns.route("/providers")
@api.response(200, "Success")
class ListAAAProviders(Resource):
    def get(self):
        """
        Get a list of AAA providers.
        """
        retval = []
        for name, aaa_provider in aaa_providers.items():
            retval.append(
                {
                    "name": aaa_provider._name,
                    "type": aaa_provider._type,
                    "display_name": aaa_provider._display_name,
                }
            )
        return retval
