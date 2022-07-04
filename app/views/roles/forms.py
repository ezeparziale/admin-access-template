from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from ...models import Permission, Role


class CreateRoleForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=30)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(min=2, max=120)]
    )
    permissions = SelectMultipleField(
        "Permissions",
        coerce=int,
    )
    submit = SubmitField("Create")

    def __init__(self, *args, **kwargs):
        super(CreateRoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    def validate_name(self, field):
        if Role.query.filter_by(name=field.data).first():
            raise ValidationError("Role name already exists.")


class EditRoleForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=30)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(min=2, max=120)]
    )
    permissions = SelectMultipleField(
        "Permissions",
        coerce=int,
    )
    submit = SubmitField("Update")

    def __init__(self, *args, **kwargs):
        super(EditRoleForm, self).__init__(*args, **kwargs)
        self.permissions.choices = [(p.id, p.name) for p in Permission.query.all()]

    # def validate_name(self, field):
    #     if Role.query.filter_by(name=field.data).first():
    #         raise ValidationError("Role name already exists.")
