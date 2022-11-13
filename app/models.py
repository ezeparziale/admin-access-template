from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, redirect, url_for
from flask_babel import format_datetime
from flask_login import UserMixin, current_user
from sqlalchemy import BOOLEAN, Column, ForeignKey, Integer, String, Table
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app import cache, db, login_manager
from app.config import settings


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(40), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    confirmed = Column(BOOLEAN, default=False)
    locale = Column(String, nullable=False, default=settings.DEFAULT_LANGUAGE)
    timezone = Column(String, nullable=True)
    last_seen = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"{self.username} : {self.email} : {self.created_at}"

    def ping(self):
        self.last_seen = datetime.utcnow()
        self.update()

    def get_token(self, expires_sec=300):
        encoded = jwt.encode(
            {
                "user_id": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return encoded

    def get_confirm_token(self, expires_sec=300):
        encoded = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return encoded

    def confirm(self, token):
        try:
            decode = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            if decode.get("confirm") != self.id:
                return False
            self.confirmed = True
            self.update()
            return True
        except:
            return None

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": format_datetime(self.created_at, format="long"),
            "roles": [(role.id, role.name) for role in self.roles],
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def add_role(self, role):
        self.roles.append(role)
        self.update()
        cache.delete_memoized(self.has_role)
        cache.delete_memoized(self.has_role_permission)

    def remove_role(self, role):
        self.roles.remove(role)
        self.update()
        cache.delete_memoized(self.has_role)
        cache.delete_memoized(self.has_role_permission)

    @cache.memoize(300)
    def has_role(self, role_name):
        for role in self.roles:
            if role.name == role_name:
                return True
        return False

    @cache.memoize(300)
    def has_role_permission(self, role_name, permission_name):
        for role in self.roles:
            if role.name == role_name:
                for permission in role.permissions:
                    if permission.name == permission_name:
                        return True
        return False

    def is_admin(self):
        return self.has_role("admin")

    def set_admin_role(self):
        role_admin = Role.query.get_or_404(1)
        self.add_role(role_admin)
        self.update()

    def update_locale(self, locale):
        if locale in settings.LANGUAGES:
            self.locale = locale
            self.update()
            return True
        return False

    @staticmethod
    def verify_token(token):
        try:
            decode = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user_id = decode.get("user_id")
        except:
            return None
        return User.query.get(user_id)


role_permission = Table(
    "role_permission",
    db.Model.metadata,
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("permission_id", Integer, ForeignKey("permissions.id")),
)

user_role = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("role_id", Integer, ForeignKey("roles.id")),
)


class Role(db.Model):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    description = Column(String(120), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_user = Column(Integer, ForeignKey("users.id"))
    updated_user = Column(Integer, ForeignKey("users.id"))
    permissions = db.relationship(
        "Permission", secondary=role_permission, backref="roles"
    )
    users = db.relationship("User", secondary=user_role, backref="roles")

    def __repr__(self) -> str:
        return f"{self.name} : {self.permissions} : {self.users}"

    def save(self):
        self.created_user = current_user.id
        self.updated_user = current_user.id
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.updated_at = datetime.utcnow()
        self.updated_user = current_user.id
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "permissions": [
                (permission.name, permission.color) for permission in self.permissions
            ],
            "created_at": format_datetime(self.created_at, format="long"),
        }

    @staticmethod
    def insert_default_values():
        db.session.add(Permission(name="admin", description="Admin role"))
        db.session.add(Permission(name="moderate", description="Moderator role"))
        db.session.add(Permission(name="users", description="Users role"))
        db.session.commit()


class Permission(db.Model):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True)
    name = Column(String(40), unique=True, nullable=False)
    description = Column(String(120), nullable=False)
    color = Column(String(40), nullable=False, default="ffffff")
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_user = Column(Integer, ForeignKey("users.id"))
    updated_user = Column(Integer, ForeignKey("users.id"))

    def __repr__(self) -> str:
        return f"{self.name}"

    def save(self):
        self.created_user = current_user.id
        self.updated_user = current_user.id
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.updated_at = datetime.utcnow()
        self.updated_user = current_user.id
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": format_datetime(self.created_at, format="long"),
        }

    @staticmethod
    def insert_default_values():
        db.session.add(
            Permission(name="write", description="Write permission", color="#8ac926")
        )
        db.session.add(
            Permission(name="update", description="Update permission", color="#1982c4")
        )
        db.session.add(
            Permission(name="delete", description="Delete permission", color="#ff595e")
        )
        db.session.commit()


# @event.listens_for(Role.__table__, 'after_create')
# def create_roles(*args, **kwargs):
#     db.session.add(
#         Role(
#             name="admin",
#             description="Admin role",
#             )
#     )
#     db.session.add(Role(name="moderate", description="Moderator role"))
#     db.session.add(Role(name="users", description="Users role"))
#     db.session.commit()
