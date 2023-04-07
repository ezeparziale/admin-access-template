from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_babel import _
from flask_login import current_user, login_required, login_user, logout_user

from app.config import settings
from app.models import Role, User
from app.utils.email import send_email

from .forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="templates",
    static_folder="static",
)


@auth_bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if current_user.email in settings.ADMIN_EMAIL:
            current_user.set_admin_role()
        if (
            not current_user.confirmed
            and request.endpoint
            and request.blueprint != "auth"
            and request.endpoint != "static"
        ):
            return redirect(url_for("auth.unconfirmed"))
        if current_user.blocked:
            logout_user()
            flash(_("Blocked account"), category="info")


@auth_bp.route("/unconfirmed/")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("home.home_view"))
    return render_template("unconfirmed.html")


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.home_view"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password_hash(form.password.data):
            if user.is_blocked():
                flash(_("Blocked account"), category="info")
            else:
                user.handle_successful_login()
                login_user(user, remember=form.remember_me.data)
                next = request.args.get("next")
                if next is None or not next.startswith("/"):
                    next = url_for("home.home_view")
                return redirect(next)
        else:
            if user:
                user.handle_failed_login()
            flash(_("Login error"), category="danger")
    return render_template("login.html", form=form)


def send_email_confirm(user):
    token = user.get_confirm_token()

    html_body = render_template(
        "emails/confirm_account.html", token=token, app_name=settings.SITE_NAME
    )
    text_body = ""
    subject = _("Confirm account")
    recipients = [user.email]
    sender = "noreplay@test.com"
    send_email(
        subject, sender, recipients, text_body, html_body, attachments=None, sync=False
    )


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.home_view"))
    form = RegistrationForm()
    if form.validate_on_submit():
        if not User.query.filter_by(email=form.email.data).first():
            encrypted_password = User.generate_password_hash(form.password.data)
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=encrypted_password,
            )
            user.save()
            role = Role.query.filter_by(name="users").first()
            user.add_role(role)
            if form.email.data in settings.ADMIN_EMAIL:
                role = Role.query.filter_by(name="admin").first()
                user.add_role(role)
            flash(_("Account created succefully"), category="success")
            flash(
                _("Please check your email and confirm your account"),
                category="info",
            )
            send_email_confirm(user)
            return redirect(url_for("auth.login"))
        else:
            flash(_("A user with this username already exists"), category="danger")
    return render_template("register.html", form=form)


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home.home_view"))


def send_email_reset_password(user):
    token = user.get_token()

    html_body = render_template(
        "emails/reset_password.html", token=token, app_name=settings.SITE_NAME
    )
    text_body = ""
    subject = _("Reset password")
    recipients = [user.email]
    sender = "noreplay@test.com"
    send_email(
        subject, sender, recipients, text_body, html_body, attachments=None, sync=False
    )

@auth_bp.route("/reset_password/", methods=["GET", "POST"])
def reset_password():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_email_reset_password(user)
            flash(
                _("A reset password link has been sent to you by email"),
                category="success",
            )
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("auth.register"))
    return render_template("reset_password.html", form=form)


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash(_("The reset link is invalid or has expired"), category="warning")
        return redirect(url_for("auth.reset_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = User.generate_password_hash(form.password.data)
        user.update()
        flash(_("Password changed"), category="success")
        return redirect(url_for("auth.login"))

    return render_template("change_password.html", form=form)


@auth_bp.route("/confirm/<token>", methods=["GET", "POST"])
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("home.home_view"))
    if current_user.confirm(token):
        flash(_("You have confirmed your account!"), category="success")
        return redirect(url_for("auth.login"))
    else:
        flash(_("The confirmation link is invalid or has expired"), category="danger")
    return redirect(url_for("home.home_view"))


@auth_bp.route("/confirm")
@login_required
def resend_confirmation():
    send_email_confirm(current_user)
    flash(_("A confirmation email has been sent to you by email"), category="info")
    return redirect(url_for("home.home_view"))
