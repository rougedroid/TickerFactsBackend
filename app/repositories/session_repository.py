from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, session_id: UUID):

        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        user_id: UUID,
        expires_at,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ):

        session = Session(
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.db.add(session)

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def delete(self, session: Session):

        await self.db.delete(session)
        await self.db.commit()