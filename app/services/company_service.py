from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company_repository import CompanyRepository


class CompanyService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.repo = CompanyRepository(db)

    async def search(
        self,
        query: str,
    ):

        return await self.repo.search(query)