from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt
from google.auth.exceptions import GoogleAuthError, TransportError
from google.auth.transport.requests import Request
from google.oauth2 import id_token as google_id_token
from fastapi import HTTPException, status

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


def verify_google_id_token(token: str) -> tuple[str, str]:
    if settings.google_web_client_id is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )

    try:
        claims = google_id_token.verify_oauth2_token(
            token,
            Request(),
            audience=settings.google_web_client_id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        ) from error
    except TransportError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google token verification is temporarily unavailable",
        ) from error
    except GoogleAuthError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        ) from error

    subject = claims.get("sub")
    email = claims.get("email")
    if (
        not isinstance(subject, str)
        or not isinstance(email, str)
        or claims.get("email_verified") is not True
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account must have a verified email",
        )

    return subject, email