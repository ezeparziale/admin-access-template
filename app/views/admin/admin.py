from flask import Blueprint, render_template
from flask_login import login_required

from app.decorators import admin_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static",
)

# Blueprint nested
from .permission import permission_bp

admin_bp.register_blueprint(permission_bp)

from .roles import roles_bp

admin_bp.register_blueprint(roles_bp)


from .users import users_bp

admin_bp.register_blueprint(users_bp)


@admin_bp.route("/", methods=["GET"])
@login_required
@admin_required
def admin_view():
    return render_template("admin/admin.html")
