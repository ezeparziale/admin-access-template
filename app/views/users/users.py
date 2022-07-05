from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import or_

from app.decorators import admin_required

from ...models import User

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users",
    template_folder="templates",
    static_folder="static",
)


@users_bp.route("/", methods=["GET"])
@login_required
@admin_required
def users_view():
    return render_template("users/users.html")


@users_bp.route("/get_data", methods=["GET"])
@login_required
@admin_required
def get_users_data():
    query = User.query

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            or_(
                User.username.like(f"%{search}%"),
                User.email.like(f"%{search}%"),
            )
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f"order[{i}][column]")
        if col_index is None:
            break
        col_name = request.args.get(f"columns[{col_index}][data]")
        if col_name not in ["username", "email"]:
            col_name = "username"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        col = getattr(User, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        "data": [user.to_dict() for user in query],
        "recordsFiltered": total_filtered,
        "recordsTotal": User.query.count(),
        "draw": request.args.get("draw", type=int),
    }
