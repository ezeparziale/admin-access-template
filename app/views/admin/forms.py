from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from sqlalchemy import and_
from wtforms import HiddenField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import Permission, Role


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
