from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from ...models import Permission


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
