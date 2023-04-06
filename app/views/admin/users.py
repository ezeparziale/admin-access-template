from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy import or_, and_, func

from app import bcrypt, db
from app.decorators import admin_required
from app.models import User, Role

from .forms import CreateUserForm, EditUserForm

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
    return render_template("users/list_users.html")


@users_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()

    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data,
            email=form.email.data,
            confirmed=form.confirmed.data,
            password=encrypted_password,
            roles=Role.query.filter(
                Role.id.in_(form.roles.data)
            ).all(),
        )
        user.save()
        return redirect(url_for("admin.users.users_view"))

    return render_template("users/create.html", form=form)


@users_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(id):
    user = db.get_or_404(User, id)

    form = EditUserForm()

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.roles = Role.query.filter(Role.id.in_(form.roles.data)).all()
        user.update()
        return redirect(url_for("admin.users.users_view"))

    form.id.data = user.id
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.roles.data = [p.id for p in user.roles]

    return render_template("users/edit.html", form=form)


@users_bp.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_user(id):
    user = db.get_or_404(User, id)
    user.delete()
    return redirect(url_for("admin.users.users_view"))


@users_bp.route("/get_data", methods=["GET"])
@login_required
@admin_required
def get_users_data():
    query = User.query

    # created_at filter
    created_at_filter = request.args.get("columns[2][search][value]", "")

    if created_at_filter:
        created_at_filter_from, created_at_filter_to = created_at_filter.split(",")
        query = query.filter(
            and_(
                func.date(User.created_at) >= created_at_filter_from,
                func.date(User.created_at) <= created_at_filter_to,
            )
        )

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            or_(
                User.username.like(f"%{search}%"),
                User.email.like(f"%{search}%"),
                User.roles.any(Role.name.like(f"%{search}%")),
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
