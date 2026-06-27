from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc
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
    
    async def get_latest(
    self,
    limit: int = 20,
):

        result = await self.db.execute(
            select(Filing)
            .order_by(
                desc(Filing.filing_time)
            )
            .limit(limit)
        )

        return result.scalars().all()
    async def get_company_filings(
    self,
    cik: str,
    limit: int = 50,
):

        result = await self.db.execute(
            select(Filing)
            .where(
                Filing.cik == cik
            )
            .order_by(
                desc(Filing.filing_time)
            )
            .limit(limit)
        )

        return result.scalars().all()