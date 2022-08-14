from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app.decorators import admin_required

from ...models import Permission
from .forms import EditPermissionForm, PermissionForm

permission_bp = Blueprint(
    "permissions",
    __name__,
    url_prefix="/permissions",
    template_folder="templates",
    static_folder="static",
)


@permission_bp.route("/", methods=["GET"])
@login_required
@admin_required
def permissions_view():
    return render_template("permissions/list.html")


@permission_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def permissions_create():
    form = PermissionForm()

    if form.validate_on_submit():
        permission = Permission(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data,
        )
        permission.save()
        return redirect(url_for("admin.permissions.permissions_view"))

    return render_template("permissions/create.html", form=form)


@permission_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_role(id):
    permission = Permission.query.get_or_404(id)
    form = EditPermissionForm()

    if form.validate_on_submit():
        permission.name = form.name.data
        permission.description = form.description.data
        permission.color = form.color.data
        permission.update()
        return redirect(url_for("admin.permissions.permissions_view"))

    form.id.data = permission.id
    form.name.data = permission.name
    form.description.data = permission.description
    form.color.data = permission.color
    return render_template("permissions/edit.html", form=form)


@permission_bp.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_permission(id):
    permission = Permission.query.get_or_404(id)
    permission.delete()
    return redirect(url_for("admin.permissions.permissions_view"))


@permission_bp.route("/get_data", methods=["GET"])
@login_required
@admin_required
def get_data_permission():
    query = Permission.query

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            or_(
                Permission.name.like(f"%{search}%"),
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
        if col_name not in ["name"]:
            col_name = "name"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        col = getattr(Permission, col_name)
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
        "recordsTotal": Permission.query.count(),
        "draw": request.args.get("draw", type=int),
    }
