from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

import jwt
from flask import redirect, request, url_for
from flask.typing import ResponseValue
from flask_babel import format_datetime
from flask_login import UserMixin, current_user
from sqlalchemy import BOOLEAN, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from app import bcrypt, cache, db, login_manager
from app.config import settings


@login_manager.user_loader
def load_user(user_id) -> Optional["User"]:
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized() -> ResponseValue:
    return redirect(url_for("auth.login", next=request.path))


class User(db.Model, UserMixin):  # type: ignore  # noqa
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    blocked: Mapped[bool] = mapped_column(BOOLEAN, default=False, nullable=False)
    login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_login_attempt: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    block_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    confirmed: Mapped[bool] = mapped_column(BOOLEAN, default=False, nullable=False)
    locale: Mapped[str] = mapped_column(
        String, default=settings.DEFAULT_LANGUAGE, nullable=False
    )
    timezone: Mapped[str] = mapped_column(String, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email}, blocked={self.blocked}, created_at={self.created_at})"  # noqa: E501

    def ping(self) -> None:
        self.last_seen = datetime.utcnow()
        self.update()

    def get_token(self, expires_sec: int = 300) -> str:
        encoded = jwt.encode(
            {
                "user_id": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return encoded

    def get_confirm_token(self, expires_sec: int = 300) -> str:
        encoded = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec),
            },
            settings.SECRET_KEY,
            algorithm="HS256",
        )
        return encoded

    def confirm(self, token: str) -> bool | None:
        try:
            decode = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if decode.get("confirm") != self.id:
                return False
            self.confirmed = True
            self.update()
            return True
        except:  # noqa: E722
            return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": format_datetime(self.created_at, format="long"),
            "roles": [(role.id, role.name) for role in self.roles],
            "blocked": self.blocked,
        }

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def block_account(self) -> None:
        self.blocked = True
        self.update()

    def unblock_account(self) -> None:
        self.blocked = False
        self.update()

    def add_role(self, role: "Role") -> None:
        self.roles.append(role)
        self.update()
        cache.delete_memoized(self.has_role)
        cache.delete_memoized(self.has_role_permission)

    def remove_role(self, role: "Role") -> None:
        self.roles.remove(role)
        self.update()
        cache.delete_memoized(self.has_role)
        cache.delete_memoized(self.has_role_permission)

    @cache.memoize(300)
    def has_role(self, role_name: str) -> bool:
        for role in self.roles:
            if role.name == role_name:
                return True
        return False

    @cache.memoize(300)
    def has_role_permission(self, role_name: str, permission_name: str) -> bool:
        for role in self.roles:
            if role.name == role_name:
                for permission in role.permissions:
                    if permission.name == permission_name:
                        return True
        return False

    def is_admin(self):
        return self.has_role("admin")

    def set_admin_role(self) -> None:
        role_admin = Role.query.get_or_404(1)
        self.add_role(role_admin)
        self.update()

    def update_locale(self, locale: str) -> bool:
        if locale in settings.LANGUAGES:
            self.locale = locale
            self.update()
            return True
        return False

    @staticmethod
    def verify_token(token: str) -> Union["User", None]:
        try:
            decode = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decode.get("user_id")
        except:  # noqa: E722
            return None
        return User.query.get(user_id)

    def check_password_hash(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return bcrypt.generate_password_hash(password).decode("utf-8")

    def handle_failed_login(self):
        self.login_attempts += 1
        self.last_login_attempt = datetime.utcnow()
        if self.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            self.blocked = True
            self.block_time = datetime.utcnow()
        self.update()

    def handle_successful_login(self):
        self.login_attempts = 0
        self.last_login_attempt = None
        self.blocked = False
        self.block_time = None
        self.update()

    def is_blocked(self):
        if self.blocked:
            if self.block_time is None:
                return True
            elif datetime.now(timezone.utc) >= self.block_time + settings.BLOCK_TIME:
                self.blocked = False
                self.block_time = None
                self.login_attempts = 0
                self.update()
                return False
            else:
                return True
        else:
            return False


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


class Role(db.Model):  # type: ignore  # noqa
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_user: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    updated_user: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission", secondary=role_permission, backref="roles"
    )
    users: Mapped[List["User"]] = relationship(
        "User", secondary=user_role, backref="roles"
    )

    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name}, description={self.description}, created_at={self.created_at}, permissions={self.permissions}, users={self.users})"  # noqa: E501

    def save(self) -> None:
        self.created_user = current_user.id
        self.updated_user = current_user.id
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        self.updated_at = datetime.utcnow()
        self.updated_user = current_user.id
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
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
    def insert_default_values() -> None:
        db.session.add(Permission(name="admin", description="Admin role"))
        db.session.add(Permission(name="moderate", description="Moderator role"))
        db.session.add(Permission(name="users", description="Users role"))
        db.session.commit()


class Permission(db.Model):  # type: ignore  # noqa
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(40), nullable=False, default="ffffff")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    created_user: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    updated_user: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    def __repr__(self) -> str:
        return f"Permission(id={self.id}, name={self.name}, description={self.description}, color={self.color}, created_at={self.created_at})"  # noqa: E501

    def save(self) -> None:
        self.created_user = current_user.id
        self.updated_user = current_user.id
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        self.updated_at = datetime.utcnow()
        self.updated_user = current_user.id
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": format_datetime(self.created_at, format="long"),
        }

    @staticmethod
    def insert_default_values() -> None:
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
