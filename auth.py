from functools import wraps
from flask import session, redirect, url_for, request, current_app


def login_required(f):
    """Decorator to protect admin and API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            if request.is_json or request.path.startswith("/api/"):
                from flask import jsonify
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def check_credentials(username, password):
    """Validate against env var credentials."""
    return (
        username == current_app.config["ADMIN_USER"]
        and password == current_app.config["ADMIN_PASS"]
    )
