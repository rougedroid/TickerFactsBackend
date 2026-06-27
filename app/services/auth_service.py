from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.google import verify_google_token
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
)
from app.repositories.user_repository import UserRepository


class AuthService:

    def __init__(self, db: AsyncSession):

        self.users = UserRepository(db)

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

        access = create_access_token(str(user.id))
        refresh = create_refresh_token(str(user.id))

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
        }
