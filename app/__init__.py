from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from .config import settings

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
login_manager.needs_refresh_message = (
    "Por favor vuelva a loguearse!!!"
)
login_manager.needs_refresh_message_category = "info"

# Mail
mail = Mail(app)

# Moment
moment = Moment(app)

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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500