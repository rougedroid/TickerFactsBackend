from fastapi import APIRouter, Depends

from app.auth.pipeline import verify_pipeline_key
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.company import CompanyCreate, CompanyResponse
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/internal",
    tags=["Internal"],
    dependencies=[
        Depends(verify_pipeline_key)
    ],
)

@router.post(
    "/company",
    response_model=CompanyResponse,
)
async def create_company(
    company: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):

    service = CompanyService(db)

    existing = await service.get_company(
        company.ticker
    )

    if existing:
        return existing

    return await service.create_company(
        ticker=company.ticker,
        cik=company.cik,
        name=company.name,
        exchange=company.exchange,
        sector=company.sector,
        industry=company.industry,
    )


