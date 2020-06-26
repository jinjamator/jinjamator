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

from passlib.hash import argon2
import jwt
from datetime import datetime
from calendar import timegm
from jinjamator.daemon.database import db
from jinjamator.daemon.app import app
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, backref
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
import logging

log = logging.getLogger("")
from sqlalchemy_serializer import SerializerMixin

logging.getLogger("serializer").setLevel(logging.ERROR)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    __bind_key__ = "aaa"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    aaa_provider = db.Column(db.String(128))
    roles = relationship("JinjamatorRole", secondary="user_role_link")
    serialize_rules = ("-password_hash",)

    @staticmethod
    def hash_password(password):
        return argon2.hash(password)

    def verify_password(self, password):
        return argon2.verify(password, self.password_hash)

    def generate_auth_token(self, expires_in=None):
        if not expires_in:
            expires_in = app.config["JINJAMATOR_AAA_TOKEN_LIFETIME"]
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
            log.info("InvalidSignatureError token invalid")
            return False
        except ExpiredSignatureError:
            log.info("ExpiredSignatureError token expired")
            return False
        except DecodeError:
            log.info("DecodeError token invalid")
            return False

        return data


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
    nonce = db.Column(db.String(128))


class JinjamatorToken(db.Model, SerializerMixin):
    __tablename__ = "token"
    __bind_key__ = "aaa"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    expires_at = db.Column(db.Integer)
    expires_in = db.Column(db.Integer)
    access_token = db.Column(db.String(4096))


class JinjamatorRole(db.Model, SerializerMixin):
    __tablename__ = "roles"
    __bind_key__ = "aaa"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(4096), unique=True)


class UserRoleLink(db.Model, SerializerMixin):
    __tablename__ = "user_role_link"
    __bind_key__ = "aaa"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
