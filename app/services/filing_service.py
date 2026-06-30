from sqlalchemy.ext.asyncio import AsyncSession
from app.models.metric import Metric
from app.repositories.metric_repository import MetricRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.filing_repository import FilingRepository



def extract_metrics(processed_info: dict, accession_number: str) -> list[Metric]:
        metric_rows = []

        for metric_name, value in processed_info.items():
            metric = Metric(
                accession_number=accession_number,
                metric_name=metric_name,
                metric_category=None,
                numeric_value=None,
                text_value=None,
                boolean_value=None,
                unit=None,
                period=None,
            )

            if isinstance(value, bool):
                metric.boolean_value = value
            elif isinstance(value, (int, float)):
                metric.numeric_value = value
            elif value is not None:
                metric.text_value = str(value)

            metric_rows.append(metric)

        return metric_rows

    
class FilingService:

    def __init__(
        self,
        db: AsyncSession,
    ):

        self.filings = FilingRepository(db)

        self.companies = CompanyRepository(db)
        self.metrics = MetricRepository(db)

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

        created_filing = await self.filings.create(
            accession_number=filing.accession_number,
            cik=filing.cik,
            form_type=filing.form_type,
            filer_type=filing.filer_type,
            filing_time=filing.filing_time,
            processed_info=filing.processed_info,
            filing_url=filing.filing_url,
        )

        metric_rows = extract_metrics(
            created_filing.processed_info,
            created_filing.accession_number,
        )

        # for metric in filing.metrics:

        #     metric_rows.append(
        #         Metric(
        #             accession_number=created_filing.accession_number,
        #             metric_name=metric.metric_name,
        #             metric_category=metric.metric_category,
        #             numeric_value=metric.numeric_value,
        #             text_value=metric.text_value,
        #             boolean_value=metric.boolean_value,
        #             unit=metric.unit,
        #             period=metric.period,
        #         )
        #     )

        if metric_rows:
            await self.metrics.bulk_create(metric_rows)

        return created_filing

    async def latest(
        self,
        limit: int = 20,
    ):

        return await self.filings.get_latest(
            limit
        )

    async def company_filings(
    self,
    ticker: str,
    limit: int = 50,
):

        company = await self.companies.get_company(
            ticker
        )

        if company is None:

            raise ValueError(
                "Company not found."
            )

        return await self.filings.get_company_filings(
            company.cik,
            limit,
        )
    
    async def get(
    self,
    accession_number: str,
):

        filing = await self.filings.get_by_accession(
            accession_number
        )

        if filing is None:

            raise ValueError(
                "Filing not found."
            )

        return filing
    
    