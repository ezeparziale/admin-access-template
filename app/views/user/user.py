from flask import Blueprint, render_template
from flask_login import login_required

from app.models import User

user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user",
    template_folder="templates",
    static_folder="static",
)


@user_bp.route("/<username>", methods=["GET", "POST"])
@login_required
def user_view(username: str):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user/user.html", user=user)
