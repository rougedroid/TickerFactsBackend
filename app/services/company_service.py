from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company_repository import CompanyRepository


class CompanyService:

    def __init__(self, db: AsyncSession):

        self.company_repo = CompanyRepository(db)

    async def get_company(
        self,
        ticker: str,
    ):
        return await self.company_repo.get_by_ticker(
            ticker
        )

    async def create_company(
        self,
        **kwargs,
    ):
        return await self.company_repo.create(
            **kwargs
        )