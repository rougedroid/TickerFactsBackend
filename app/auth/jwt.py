from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def _create_token(
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    session_id: str | None = None,
) -> str:

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": token_type,
        "ver": 1,
        "iat": now,
        "exp": now + expires_delta,
    }

    if session_id is not None:
        payload["sid"] = session_id

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def create_access_token(subject: str) -> str:

    return _create_token(
        subject=subject,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(
    subject: str,
    session_id: str,
) -> str:

    return _create_token(
        subject=subject,
        expires_delta=timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        token_type="refresh",
        session_id=session_id,
    )

def decode_token(token: str) -> dict:

    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
