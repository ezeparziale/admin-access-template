from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required("admin")(f)

def moderate_required(f):
    return role_required("moderate")(f)


def role_permission_required(role_name, permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role_permission(role_name, permission_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def moderate_permission_required(permission_name):
    return role_permission_required("moderate", permission_name)