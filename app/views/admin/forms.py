from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from ...models import Permission, Role


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
        render_kw={"data-placeholder": lazy_gettext("Choose anything")},
    )
    submit = SubmitField(lazy_gettext("Create"))

    def __init__(self, *args, **kwargs):
        super(CreateRoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    def validate_name(self, field):
        if Role.query.filter_by(name=field.data).first():
            raise ValidationError(lazy_gettext("Role name already exists."))


class EditRoleForm(FlaskForm):
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
        super(EditRoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    # def validate_name(self, field):
    #     if Role.query.filter_by(name=field.data).first():
    #         raise ValidationError("Role name already exists.")