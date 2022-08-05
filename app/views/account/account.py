from flask import Blueprint, flash, jsonify, make_response, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import or_
from flask_babel import _

from app.decorators import admin_required

from ...models import User

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
        return make_response(jsonify({"status":True}), 200)
    else:
        return make_response(jsonify({"status":False}), 200)