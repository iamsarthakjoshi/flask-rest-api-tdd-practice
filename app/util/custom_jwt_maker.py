import os
import jwt
import datetime

from flask import current_app
from app.constants import TokenType

SECRET_KEY = os.getenv("SECRET_KEY", "dark-secret-here")


def encode_jwt(token_type, user_id):
    """Create JSON Web Token which uses HS256 algorithm and custom Secret Key for enconding.
    This particualr Secret Key must be used by other services inorder to decode this token for validation.

    Arguments:
        token_type {string} -- [For Example: refresh_token, access_token, reset_password, email_verification]
        user_id {integer} -- [User Id]
    Returns:
        [string] -- [token string]
    """
    try:
        if token_type == TokenType.RESET_PASSWORD:
            seconds = os.getenv("RESET_PASSWORD_TOKEN_EXP_SECONDS")
        elif token_type == TokenType.EMAIL_VERIFICATION:
            seconds = os.getenv("EMAIL_VERIFICATION_TOKEN_EXP_SECONDS")
        elif token_type == TokenType.REFRESH_TOKEN:
            seconds = os.getenv("REFRESH_TOKEN_EXP_SECONDS")
        elif token_type == TokenType.ACCESS_TOKEN:
            seconds = os.getenv("ACCESS_TOKEN_EXP_SECONDS")

        if current_app.config["TESTING"]:
            seconds = 5

        # create a payload
        payload = {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(seconds=int(seconds)),
            "iat": datetime.datetime.utcnow(),
            "uid": user_id,
        }
        # return token
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode("utf-8")
    except Exception as e:
        return e


def decode_jwt(token):
    """Decodes JSON Web Token which uses HS256 algorithm and custom Secret Key for decoding.

    Arguments:
        - token: string
    Returns:
        - payload: object
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"decoded": True, "payload": payload} if payload else None
    except jwt.ExpiredSignatureError:
        return {"decoded": False, "message": "Expired token. Please log in again."}
    except jwt.InvalidTokenError:
        return {"decoded": False, "message": "Invalid token. Please log in again."}
    except Exception as e:
        return {"decoded": False, "message": str(e)}
