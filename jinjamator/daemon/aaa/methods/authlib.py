from . import AuthProviderBase
import logging
log = logging.getLogger()
from authlib.integrations.flask_client import OAuth, OAuthError
from jinjamator.daemon.aaa.models import (
    User,
    Oauth2UpstreamToken,
    JinjamatorToken,
    JinjamatorRole,
)
from flask import g, url_for, abort
from copy import deepcopy
from functools import wraps
import random
from pprint import pformat
from glob import glob
import os
from copy import deepcopy
from jwt import InvalidSignatureError, ExpiredSignatureError
from jinjamator.daemon.app import app
from jinjamator.daemon.database import db
from datetime import datetime
from calendar import timegm
import string




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

