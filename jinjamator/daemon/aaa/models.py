# from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import argon2
import jwt
from datetime import datetime
from calendar import timegm
from jinjamator.daemon.database import db
from jinjamator.daemon.app import app
from sqlalchemy.inspection import inspect

from jwt import InvalidSignatureError, ExpiredSignatureError
import logging

log = logging.getLogger("")


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class User(db.Model, Serializer):
    __tablename__ = "users"
    __bind_key__ = "aaa"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    aaa_provider = db.Column(db.String(128))

    @staticmethod
    def hash_password(password):
        return argon2.hash(password)

    def verify_password(self, password):
        return argon2.verify(password, self.password_hash)

    def generate_auth_token(self, expires_in=600):
        now = timegm(datetime.utcnow().utctimetuple())

        exp = now + expires_in
        jwt_token = jwt.encode(
            {"id": self.id, "exp": exp, "iat": now},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

        token = JinjamatorToken()
        token.user_id = self.id
        token.expires_in = expires_in
        token.expires_at = exp
        token.access_token = jwt_token.decode(encoding="UTF-8")
        db.session.merge(token)
        db.session.commit()

        return token

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        except InvalidSignatureError:
            log.info("token invalid")
            return False
        except ExpiredSignatureError:
            log.info("token expired")
            return False
        return data

    def serialize(self):
        d = Serializer.serialize(self)
        del d["password_hash"]
        return d


class Oauth2UpstreamToken(db.Model):
    __tablename__ = "oauth2_upstream_token"
    __bind_key__ = "aaa"

    aaa_provider = db.Column(db.String(128))
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    access_token = db.Column(db.String(4096))
    expires_at = db.Column(db.Integer)
    expires_in = db.Column(db.Integer)
    id_token = db.Column(db.String(4096))
    scope = db.Column(db.String(128))
    token_type = db.Column(db.String(128))
    user = db.relationship("User")


class JinjamatorToken(db.Model, Serializer):
    __tablename__ = "token"
    __bind_key__ = "aaa"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    expires_at = db.Column(db.Integer)
    expires_in = db.Column(db.Integer)
    access_token = db.Column(db.String(4096))
