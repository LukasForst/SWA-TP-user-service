import datetime
from typing import Tuple, Optional

import jwt
from flask_bcrypt import Bcrypt

from common.Config import get_config

bcrypt = Bcrypt()


def encode_password(password: str) -> str:
    return bcrypt.generate_password_hash(password).decode()


def compare_passwords(pwd_hash: str, password: str) -> bool:
    return bcrypt.check_password_hash(pwd_hash, password)


def encode_auth_token(user) -> bytearray:
    """
    Generates the Auth Token
    """
    payload = {
        'user_id': user.id,
        'user_mail': user.email,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(
        payload,
        get_config().jwt_secret,
        algorithm='HS256'
    )


def decode_auth_token(auth_token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Validates the auth token
    """
    try:
        payload = jwt.decode(auth_token, get_config().jwt_secret)
        return int(payload['user_id']), None
    except jwt.ExpiredSignatureError:
        return None, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return None, 'Invalid token. Please log in again.'
