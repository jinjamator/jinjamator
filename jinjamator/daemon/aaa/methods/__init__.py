import logging
log = logging.getLogger()
from jinjamator.daemon.app import app
from jinjamator.daemon.database import db
from jinjamator.daemon.aaa.models import (
    User,
    Oauth2UpstreamToken,
    JinjamatorToken,
    JinjamatorRole,
)

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

