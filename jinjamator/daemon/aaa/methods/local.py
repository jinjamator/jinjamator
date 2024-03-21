import logging
log = logging.getLogger()
from jinjamator.daemon.aaa.models import (
    User,
    Oauth2UpstreamToken,
    JinjamatorToken,
    JinjamatorRole,
)
from jinjamator.daemon.app import app
from jinjamator.daemon.database import db

from . import AuthProviderBase

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
