from functools import wraps
from flask import request, jsonify
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import os


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == "OPTIONS":
            return '', 204  # Allow preflight

        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        secret = os.getenv("JWT_SECRET_KEY")  # should match what you used to sign tokens

        try:
            # Decode and validate JWT
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            print("✅ Token valid, payload:", payload)

            # You can also attach user info to request context if you want:
            request.user = payload
            request.user_headers = build_user_headers(payload)

        except ExpiredSignatureError:
            print("❌ Token expired")
            return jsonify({"message": "Token has expired"}), 401

        except InvalidTokenError:
            print("❌ Invalid token")
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)
    return decorated

def build_user_headers(payload: dict) -> dict:
    """
    Build custom headers from JWT payload to propagate user info.
    Equivalent to Feign interceptor adding X_USER_ID, X_EMAIL, X_ROLES.
    """
    headers = {}

    if "sub" in payload:
        headers["X-USER-ID"] = payload["sub"]
    if "email" in payload:
        headers["X-EMAIL"] = payload["email"]
    if "role" in payload:
        headers["X-ROLES"] = payload["role"]
    if "fullName" in payload:
        headers["X-FULL-NAME"] = payload["fullName"]

    return headers

