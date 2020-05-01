from flask_login import current_user
from flask import abort
from functools import wraps

def admin_required():
    """Restrict a view to admins."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.admin:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
