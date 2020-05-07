# from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import argon2
import jwt
import time
from jinjamator.daemon.database import db
from jinjamator.daemon.app import app


class User(db.Model):
    __tablename__ = 'users'
    __bind_key__ = 'aaa'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    aaa_provider = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = argon2.hash(password)

    def verify_password(self, password):
        return argon2.verify(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])