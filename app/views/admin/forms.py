from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from sqlalchemy import and_
from wtforms import HiddenField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

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
        if Permission.query.filter_by(name=field.data).first():
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

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        check_permission_exists = Permission.query.filter(
            and_(Permission.name == self.name.data, Permission.id != self.id.data)
        ).all()

        if check_permission_exists:
            self.name.errors.append(
                f"Permission: '{self.name.data}' name already exists."
            )
            return False

        return True


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
        if Role.query.filter_by(name=field.data).first():
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

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        check_role_exists = Role.query.filter(
            and_(Role.name == self.name.data, Role.id != self.id.data)
        ).all()

        if check_role_exists:
            self.name.errors.append(f"Role: '{self.name.data}' name already exists.")
            return False

        return True
