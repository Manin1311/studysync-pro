from functools import wraps
from flask import jsonify, request
from flask_login import current_user

def api_login_required(f):
    """Custom decorator for API routes that returns JSON errors instead of redirects"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        try:
            is_authenticated = current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False
            if not is_authenticated:
                return jsonify({'error': 'Unauthorized. Please log in.'}), 401
        except Exception as e:
            return jsonify({'error': 'Session error. Please log in again.'}), 401
        return f(*args, **kwargs)
    return decorated_function

