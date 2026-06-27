from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filing import Filing


class FilingRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_accession(
        self,
        accession_number: str,
    ):

        result = await self.db.execute(
            select(Filing).where(
                Filing.accession_number == accession_number
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        **kwargs,
    ):

        filing = Filing(**kwargs)

        self.db.add(filing)

        await self.db.commit()

        await self.db.refresh(filing)

        return filing