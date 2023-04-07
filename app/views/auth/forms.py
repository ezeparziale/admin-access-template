from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField(
        label=lazy_gettext("Username"),
        validators=[DataRequired(), Length(min=3, max=20)],
    )
    email = StringField(
        label=lazy_gettext("Email"), validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        label=lazy_gettext("Password"),
        validators=[DataRequired(), Length(min=6, max=16)],
    )
    confirm_password = PasswordField(
        label=lazy_gettext("Confirm password"),
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField(label=lazy_gettext("Sign up"))


class LoginForm(FlaskForm):
    email = StringField(
        label=lazy_gettext("Email"), validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        label=lazy_gettext("Password"),
        validators=[DataRequired(), Length(min=6, max=16)],
    )
    remember_me = BooleanField(label=lazy_gettext("Remember me"))
    submit = SubmitField(label=lazy_gettext("Log in"))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        label=lazy_gettext("Email"), validators=[DataRequired(), Email()]
    )
    submit = SubmitField(label=lazy_gettext("Reset password"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label=lazy_gettext("Password"),
        validators=[DataRequired(), Length(min=6, max=16)],
    )
    confirm_password = PasswordField(
        label=lazy_gettext("Confirm password"),
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField(label=lazy_gettext("Change password"))
