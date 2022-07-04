from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required

from app.decorators import admin_required, role_permission_required, moderate_required
from ...models import Role, Permission, User
from ...config import settings
from .forms import CreateRoleForm, EditRoleForm
from sqlalchemy import or_

roles_bp = Blueprint(
    "roles", 
    __name__, 
    url_prefix="/roles",
    template_folder="templates",
    static_folder="static"
)


@roles_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def roles_view():
    user_roles = Role.query.all()
    return render_template("roles/list.html", user_roles=user_roles)


@roles_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_role():
    form = CreateRoleForm()

    if form.validate_on_submit():
        role = Role(
            name=form.name.data,
            description=form.description.data,
            permissions = Permission.query.filter(Permission.id.in_(form.permissions.data)).all()
        )
        role.save()
        return redirect(url_for("roles.roles_view"))

    return render_template("roles/create.html", form=form)

@roles_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_role(id):
    role = Role.query.get_or_404(id)
    form = EditRoleForm()

    if form.validate_on_submit():
        print(form.permissions.data)
        role.name = form.name.data
        role.description = form.description.data
        role.permissions = Permission.query.filter(Permission.id.in_(form.permissions.data)).all()
        role.update()
        return redirect(url_for("roles.roles_view"))

    form.name.data = role.name
    form.description.data = role.description
    form.permissions.data = [p.id for p in role.permissions] 
    return render_template("roles/edit.html", form=form)


@roles_bp.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_role(id):
    role = Role.query.get_or_404(id)
    role.delete()
    return redirect(url_for("roles.roles_view"))


@roles_bp.route("/delete_user/<int:role_id>/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_role_from_user(role_id, user_id):
    role = Role.query.get_or_404(role_id)
    user = User.query.get_or_404(user_id)
    user.remove_role(role)
    return redirect(url_for("roles.view_role", id=role_id))

@roles_bp.route("/add_user/<int:role_id>/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def add_user_to_role(role_id, user_id):
    role = Role.query.get_or_404(role_id)
    user = User.query.get_or_404(user_id)
    user.add_role(role)
    return redirect(url_for("roles.view_role", id=role_id))

@roles_bp.route("/add_user_role/<int:role_id>", methods=["GET", "POST"])
@login_required
@admin_required
def add_user_role(role_id):
    role = Role.query.get_or_404(role_id)
    return render_template("roles/add_user_role.html", role=role)

@roles_bp.route("/view/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def view_role(id):
    role = Role.query.get_or_404(id)
    return render_template("roles/view.html", role=role)


@roles_bp.route("/get_data", methods=["GET"])
@login_required
@admin_required
def get_data():
    query = Role.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(or_(
            Role.name.like(f'%{search}%'),
            Role.permissions.any(Permission.name.like(f'%{search}%'))
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['name', 'permissions']:
            col_name = 'name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Role, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Role.query.count(),
        'draw': request.args.get('draw', type=int),
    }


@roles_bp.route("/get_data_users/<int:id>", methods=["GET"])
@login_required
@admin_required
def get_data_users(id):
    query = User.query.filter(User.roles.any(Role.id == id))

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(or_(
            User.username.like(f'%{search}%'),
            User.email.like(f'%{search}%'),
        ))
    print(query)

    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['username', 'email']:
            col_name = 'username'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(User, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [user.to_dict() for user in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': User.query.count(),
        'draw': request.args.get('draw', type=int),
    }

@roles_bp.route("/eze", methods=["GET", "POST"])
# @moderate_required
# @admin_required
@role_permission_required("moderate", "write")
def eze():
    return jsonify({"message": "success"})