from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password):
    byte_pw=password.encode("utf-8")
    return bcrypt.hashpw(byte_pw,bcrypt.gensalt()).decode("utf-8")

def verify_password(password,password_hash):
    byte_pw=password.encode("utf-8")
    
    return bcrypt.checkpw(byte_pw,password_hash.encode("utf-8"))

def encode_jwt(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=30),
    }
    return jwt.encode(payload, settings.secret, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    return jwt.decode(
        token,
        settings.secret,
        algorithms=["HS256"],
        options={"require": ["sub", "exp"]},
    )