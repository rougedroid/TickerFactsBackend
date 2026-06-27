from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.repositories.session_repository import SessionRepository
from app.auth.google import verify_google_token
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.repositories.user_repository import UserRepository
from uuid import UUID

from app.auth.jwt import decode_token


class AuthService:

    def __init__(self, db: AsyncSession):

        self.db = db

        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)

    async def login_with_google(self, credential: str):

        google_user = verify_google_token(credential)

        if google_user is None:
            raise ValueError("Invalid Google token.")

        user = await self.users.get_by_provider_id(google_user["provider_id"])

        if user is None:

            user = await self.users.create(
                email=google_user["email"],
                name=google_user["name"],
                provider="google",
                provider_id=google_user["provider_id"],
                picture=google_user["picture"],
            )

        session = await self.sessions.create(
            user_id=user.id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=30),
        )

        access = create_access_token(str(user.id))

        refresh = create_refresh_token(
            str(user.id),
            str(session.id),
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
        }
    
    async def refresh_access_token(
        self,
        refresh_token: str,
    ):

        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token.")

        session_id = payload.get("sid")

        if session_id is None:
            raise ValueError("Invalid session.")

        session = await self.sessions.get_by_id(
            UUID(session_id)
        )

        if session is None:
            raise ValueError("Session expired.")

        user = await self.users.get_by_id(session.user_id)

        if user is None:
            raise ValueError("User not found.")

        return create_access_token(str(user.id))