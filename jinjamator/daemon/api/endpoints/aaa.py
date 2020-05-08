import logging

from flask import request, flash, url_for, g, Response
from flask import Flask, url_for, session, redirect

from flask_restx import Resource, abort
from jinjamator.daemon.api.serializers import environments
from jinjamator.daemon.aaa import aaa_providers
from jinjamator.daemon.api.restx import api
from jinjamator.daemon.api.serializers import aaa_post_data, aaa_create_user_data
from jinjamator.daemon.aaa.models import User
from jinjamator.daemon.database import db

from flask import current_app as app
import glob
import os
import xxhash
from pprint import pformat
from datetime import datetime
from calendar import timegm

log = logging.getLogger()

ns = api.namespace(
    "aaa",
    description="Operations related to jinjamator Authentication Authorization and Accounting",
)

current_provider = None


@ns.route("/login/<provider>")
class Login(Resource):
    @api.response(400, "Unknown Login Provider <provider>")
    @api.response(200, "Success")
    def get(self, provider="local"):
        """
        Login User.
        """
        if provider in aaa_providers:
            return aaa_providers[provider].login(request)
        abort(400, f"Unknown Login Provider {provider}")

    @api.expect(aaa_post_data)
    def post(self, provider="local"):
        """
        Login User.
        """
        if provider in aaa_providers:
            return aaa_providers[provider].login(request)
        abort(400, f"Unknown Login Provider {provider}")


@ns.route("/logout")
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
class Auth(Resource):
    def get(self):

        for aaa_provider in aaa_providers:
            log.debug(f"trying to use {aaa_provider}")
            if aaa_providers[aaa_provider].authorize(request):
                current_provider = aaa_providers[aaa_provider]
                token = current_provider.get_token()

                if token:
                    redir = redirect(url_for("webui.index", access_token=token))
                    return redir
                else:
                    abort(401, "Upstream token expired, please reauthenticate")

            # obj = getattr(aaa_providers[aaa_provider], aaa_provider)
            # try:
            #     access_token = obj.authorize_access_token()
            #     current_provider = obj
            #     break
            # except:
            #     pass
            # if access_token:
            #     id_token = obj.parse_id_token(access_token)
            #     log.info(f'logged in user {pformat(id_token)} with token {pformat(access_token)}')
            #     session['user'] = id_token
            #     return access_token['access_token']
        abort(400, "Cannot find valid login provider")


@ns.route("/verify")
class VerifyToken(Resource):
    @api.doc(
        params={
            "Authorization": {"in": "header", "description": "An authorization token"}
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
                    if (token_data["exp"] - now) < 300:
                        log.info("renewing token as lifetime less than 300s")
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
            abort(402, "Authorization required, no Authorization Header found")


@ns.route("/users")
class Users(Resource):
    def get(self):
        retval = []
        for user in User.query.all():
            retval.append(
                {
                    "username": user.username,
                    "name": user.name,
                    "aaa_provider": user.aaa_provider,
                }
            )
        return retval

    @api.expect(aaa_create_user_data)
    def post(self):
        try:
            new_user = User(
                username=request.json["username"],
                name=request.json["name"],
                password_hash=User.hash_password(request.json["password"]),
                aaa_provider="local",
            )
        except IndexError:
            abort(400, "Invalid request: Parameters missing, or not properly encoded")
        db.session.add(new_user)
        try:
            db.session.commit()
            db.session.refresh(new_user)
            return new_user.serialize()
        except:
            abort(400, "Invalid request: User exists")


@ns.route("/users/<user_id>")
class UserDetail(Resource):
    @api.doc(params={"user_id": "The User ID of the user which should be returned"})
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            return user
        else:
            abort(404, "User ID not found")
