from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from app.models.company import Company


class CompanyRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_ticker(self, ticker: str):

        result = await self.db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )

        return result.scalar_one_or_none()

    async def get_by_cik(
        self,
        cik: str,
    ):

        result = await self.db.execute(select(Company).where(Company.cik == cik))

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        ticker: str,
        cik: str,
        name: str,
        exchange: str | None = None,
        sector: str | None = None,
        industry: str | None = None,
    ):

        company = Company(
            ticker=ticker.upper(),
            cik=cik,
            name=name,
            exchange=exchange,
            sector=sector,
            industry=industry,
        )

        self.db.add(company)

        await self.db.commit()
        await self.db.refresh(company)

        return company
    
    async def search(
    self,
    query: str,
    limit: int = 15,
):

        result = await self.db.execute(
            select(Company)
            .where(
                or_(
                    Company.ticker.ilike(f"{query}%"),
                    Company.name.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
        )

        return result.scalars().all()
