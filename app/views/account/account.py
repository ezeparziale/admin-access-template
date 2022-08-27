from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user, login_required

account_bp = Blueprint(
    "account",
    __name__,
    url_prefix="/account",
    template_folder="templates",
    static_folder="static",
)


@account_bp.route("/change_language", methods=["POST"])
@login_required
def change_language():
    locale = request.get_json()["locale"]
    status = current_user.update_locale(locale)
    if status:
        return make_response(jsonify({"status": True}), 200)
    else:
        return make_response(jsonify({"status": False}), 200)
