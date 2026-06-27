from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.company_repository import CompanyRepository
from app.repositories.filing_repository import FilingRepository


class FilingService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.filings = FilingRepository(db)

        self.companies = CompanyRepository(db)

    async def ingest(
        self,
        filing,
    ):

        existing = await self.filings.get_by_accession(filing.accession_number)

        if existing:
            return existing

        company = await self.companies.get_by_cik(filing.cik)

        if company is None:

            raise ValueError(f"Company with CIK {filing.cik} not found.")

        return await self.filings.create(
            accession_number=filing.accession_number,
            cik=filing.cik,
            form_type=filing.form_type,
            filer_type=filing.filer_type,
            filing_time=filing.filing_time,
            processed_info=filing.processed_info,
            filing_url=filing.filing_url,
        )
