import email
from click import password_option
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegistrationForm(FlaskForm):
    username = StringField(label="USUARIO", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField(label="EMAIL", validators=[DataRequired(), Email()])
    password = PasswordField(label="PASSWORD", validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField(label="CONFIRMAR PASSWORD", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(label="Registrar")

class LoginForm(FlaskForm):
    email = StringField(label="EMAIL", validators=[DataRequired(), Email()])
    password = PasswordField(label="PASSWORD", validators=[DataRequired(), Length(min=6, max=16)])
    remember_me = BooleanField(label="Recuérdame")
    submit = SubmitField(label="Iniciar sesión")

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(label="EMAIL", validators=[DataRequired(), Email()])
    submit = SubmitField(label="Restablecer Password")

class ResetPasswordForm(FlaskForm):
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=6, max=16)])
    confirm_password = PasswordField(label="Confirma Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(label="Cambiar Password")
