from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from sqlalchemy import and_
from wtforms import (
    BooleanField,
    HiddenField,
    PasswordField,
    SelectMultipleField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Length, ValidationError

from app import db
from app.models import Permission, Role, User


class PermissionForm(FlaskForm):
    name = StringField(
        lazy_gettext("Name"),
        validators=[
            DataRequired(message=lazy_gettext("Please complete this field")),
            Length(min=2, max=30),
        ],
    )
    description = StringField(
        lazy_gettext("Description"),
        validators=[
            DataRequired(lazy_gettext("Please complete this field")),
            Length(min=2, max=120),
        ],
    )
    color = StringField(
        lazy_gettext("Color"),
        validators=[DataRequired(lazy_gettext("Please complete this field"))],
    )
    submit = SubmitField(lazy_gettext("Create"))

    def validate_name(self, field):
        check = (
            db.session.execute(db.select(Permission).filter_by(name=field.data))
            .scalars()
            .first()
        )
        if check:
            raise ValidationError(lazy_gettext("Permission name already exists."))


class EditPermissionForm(FlaskForm):
    id = HiddenField()
    name = StringField(
        lazy_gettext("Name"),
        validators=[
            DataRequired(lazy_gettext("Please complete this field")),
            Length(min=2, max=30),
        ],
    )
    description = StringField(
        lazy_gettext("Description"),
        validators=[
            DataRequired(lazy_gettext("Please complete this field")),
            Length(min=2, max=120),
        ],
    )
    color = StringField(
        lazy_gettext("Color"),
        validators=[DataRequired(lazy_gettext("Please complete this field"))],
    )
    submit = SubmitField(lazy_gettext("Update"))

    def validate_name(self, field):
        check_permission_exists = (
            db.session.execute(
                db.select(Permission).filter(
                    and_(Permission.name == field.data, Permission.id != self.id.data)
                )
            )
            .scalars()
            .first()
        )

        if check_permission_exists:
            raise ValidationError(f"Permission '{field.data}' already exists.")


class CreateRoleForm(FlaskForm):
    name = StringField(
        lazy_gettext("Name"), validators=[DataRequired(), Length(min=2, max=30)]
    )
    description = StringField(
        lazy_gettext("Description"), validators=[DataRequired(), Length(min=2, max=120)]
    )
    permissions = SelectMultipleField(
        lazy_gettext("Permissions"),
        coerce=int,
        render_kw={
            "placeholder": lazy_gettext("Choose anything"),
            "multiple": "",
            "autocomplete": "off",
        },
    )
    submit = SubmitField(lazy_gettext("Create"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    def validate_name(self, field):
        check = (
            db.session.execute(db.select(Role).filter_by(name=field.data))
            .scalars()
            .first()
        )
        if check:
            raise ValidationError(lazy_gettext("Role name already exists."))


class EditRoleForm(FlaskForm):
    id = HiddenField()
    name = StringField(
        lazy_gettext("Name"), validators=[DataRequired(), Length(min=2, max=30)]
    )
    description = StringField(
        lazy_gettext("Description"), validators=[DataRequired(), Length(min=2, max=120)]
    )
    permissions = SelectMultipleField(
        lazy_gettext("Permissions"),
        coerce=int,
        render_kw={"data-placeholder": lazy_gettext("Choose anything")},
    )
    submit = SubmitField(lazy_gettext("Update"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    def validate_name(self, field):
        check_role_exists = (
            db.session.execute(
                db.select(Role).filter(
                    and_(Role.name == field.data, Role.id != self.id.data)
                )
            )
            .scalars()
            .first()
        )

        if check_role_exists:
            raise ValidationError(f"Role '{field.data}' already exists.")


class EditUserForm(FlaskForm):
    id = HiddenField()
    username = StringField(
        lazy_gettext("Username"), validators=[DataRequired(), Length(min=2, max=30)]
    )
    email = StringField(lazy_gettext("Email"), validators=[DataRequired(), Email()])
    confirmed = BooleanField(lazy_gettext("Confirmed"))
    blocked = BooleanField(lazy_gettext("Blocked"))
    roles = SelectMultipleField(
        lazy_gettext("Roles"),
        coerce=int,
        render_kw={
            "placeholder": lazy_gettext("Choose anything"),
            "multiple": "",
            "autocomplete": "off",
        },
    )
    submit = SubmitField("Update")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles.choices = [(p.id, p.name) for p in Role.query.all()]

    def validate_username(self, field):
        check_username_exists = (
            db.session.execute(
                db.select(User).filter(
                    and_(User.username == field.data, User.id != self.id.data)
                )
            )
            .scalars()
            .first()
        )

        if check_username_exists:
            raise ValidationError(f"Username '{field.data}' already exists.")

    def validate_email(self, field):
        check_email_exists = (
            db.session.execute(
                db.select(User).filter(
                    and_(User.email == field.data, User.id != self.id.data)
                )
            )
            .scalars()
            .first()
        )

        if check_email_exists:
            raise ValidationError(f"Email '{field.data}' already exists.")


class CreateUserForm(FlaskForm):
    username = StringField(
        lazy_gettext("Username"), validators=[DataRequired(), Length(min=2, max=30)]
    )
    email = StringField(lazy_gettext("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(
        label=lazy_gettext("Password"), validators=[DataRequired(), Length(min=6, max=16)]
    )
    confirmed = BooleanField(lazy_gettext("Confirmed"))
    blocked = BooleanField(lazy_gettext("Blocked"))
    roles = SelectMultipleField(
        lazy_gettext("Roles"),
        coerce=int,
        render_kw={
            "placeholder": lazy_gettext("Choose anything"),
            "multiple": "",
            "autocomplete": "off",
        },
    )
    submit = SubmitField("Create")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roles.choices = [(p.id, p.name) for p in Role.query.all()]

    def validate_username(self, field):
        check_username_exists = (
            db.session.execute(
                db.select(User).filter(and_(User.username == field.data))
            )
            .scalars()
            .first()
        )

        if check_username_exists:
            raise ValidationError(f"_({{'Username'}}) '{field.data}' already exists.")

    def validate_email(self, field):
        check_email_exists = (
            db.session.execute(db.select(User).filter(and_(User.email == field.data)))
            .scalars()
            .first()
        )

        if check_email_exists:
            raise ValidationError(f"Email '{field.data}' already exists.")
