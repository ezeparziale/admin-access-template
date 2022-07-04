from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from ...models import Permission


class PermissionForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(min=2, max=30)
        ]
    )
    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(min=2, max=120)
        ]
    )
    color = StringField(
        "Color",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField("Create")

    def validate_name(self, field):
        if Permission.query.filter_by(name=field.data).first():
            raise ValidationError("Permission name already exists.")


class EditPermissionForm(FlaskForm):
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Length(min=2, max=30)
        ]
    )
    description = StringField(
        "Description",
        validators=[
            DataRequired(),
            Length(min=2, max=120)
        ]
    )
    color = StringField(
        "Color",
        validators=[
            DataRequired()
        ]
    )
    submit = SubmitField("Update")

