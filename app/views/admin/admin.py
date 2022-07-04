from flask import Blueprint, render_template
from flask_login import login_required

from app.decorators import admin_required


admin_bp = Blueprint(
    "admin", 
    __name__, 
    url_prefix="/admin",
    template_folder="templates",
    static_folder="static"
)

@admin_bp.route("/", methods=["GET"])
@login_required
@admin_required
def admin_view():
    return render_template("admin/admin.html")