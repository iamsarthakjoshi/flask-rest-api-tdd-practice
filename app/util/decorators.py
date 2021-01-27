from functools import wraps
from flask import request, jsonify

from app.util import is_missing_request_values

# Add authentication wrapper
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        try:
            # Parses out the "Bearer" portion
            token = auth_header.split(" ")[1]
            if not token:
                return jsonify(error="Token is missing. Please login."), 401
            decoded = verifier.decodeJWTAuthToken(token)
        except jwt.ExpiredSignatureError:
            return jsonify(error="Signature expired. Please log in again."), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token. Please log in again."), 401
        except Exception as e:
            return jsonify(error="Something went wrong internally.", details=e), 401

        kwargs["token"] = token
        kwargs["decoded"] = decoded
        return f(*args, **kwargs)

    return decorated


def sanitize_request(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        body = request.get_json()
        missing_request_values = is_missing_request_values(body=body)
        if missing_request_values:
            return jsonify(error=missing_request_values, status=404), 404
        return f(*args, **kwargs)

    return decorated
