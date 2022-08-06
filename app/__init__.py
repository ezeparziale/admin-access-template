from logging.config import dictConfig

from flask import Flask, render_template, request
from flask_babel import Babel, lazy_gettext
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from .config import settings

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
                "datefmt": "%Y-%m-%d %I:%M:%S %z",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

# Flask
app = Flask(__name__)
app.config.from_object(settings)

# Database
db = SQLAlchemy(app)
# db.create_all()

# Bcrypt
bcrypt = Bcrypt(app)

# Login Manager
login_manager = LoginManager(app)
login_manager.refresh_view = "auth.login"
login_manager.needs_refresh_message = lazy_gettext("Please log in to access this page!")
login_manager.needs_refresh_message_category = "info"

# Mail
mail = Mail(app)

# Moment
moment = Moment(app)

# Babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    if current_user.locale:
        return current_user.locale
    return request.accept_languages.best_match(app.config["LANGUAGES"])


@babel.timezoneselector
def get_timezone():
    user = getattr(g, "user", None)
    if user is not None:
        return user.timezone


# Blueprints
from .views.home import home

app.register_blueprint(home.home_bp)

from .views.auth import auth

app.register_blueprint(auth.auth_bp)

from .views.roles import roles

app.register_blueprint(roles.roles_bp)

from .views.permissions import permission

app.register_blueprint(permission.permission_bp)

from .views.users import users

app.register_blueprint(users.users_bp)

from .views.admin import admin

app.register_blueprint(admin.admin_bp)

from .views.account import account

app.register_blueprint(account.account_bp)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
