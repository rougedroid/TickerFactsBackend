from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID):

        result = await self.db.execute(select(User).where(User.id == user_id))

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str):

        result = await self.db.execute(select(User).where(User.email == email))

        return result.scalar_one_or_none()

    async def get_by_provider_id(self, provider_id: str):

        result = await self.db.execute(
            select(User).where(User.provider_id == provider_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        name: str,
        provider: str,
        provider_id: str,
        picture: str | None = None,
    ):

        user = User(
            email=email,
            name=name,
            provider=provider,
            provider_id=provider_id,
            picture=picture,
        )

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update(self, user: User, **kwargs):

        for key, value in kwargs.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user
