from flask import jsonify

def api_response(status, message=None, data=None, code=200):
    """Standardized JSON response wrapper"""
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    }), code

from functools import wraps

def token_required(f):
    """Decorator to protect API routes using a token"""
    from flask import request, current_app
    from app.models import User
    import jwt

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return api_response("error", "Token is missing", code=401)

        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token.split(" ")[1]

            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                raise Exception("User not found")

        except Exception:
            return api_response("error", "Token is invalid or expired", code=401)

        return f(current_user, *args, **kwargs)

    return decorated
