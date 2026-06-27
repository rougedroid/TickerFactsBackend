from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.company import (
    CompanyCreate,
    CompanyResponse,
)
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.get(
    "/{ticker}",
    response_model=CompanyResponse,
)
async def get_company(
    ticker: str,
    db: AsyncSession = Depends(get_db),
):

    service = CompanyService(db)

    company = await service.get_company(
        ticker
    )

    if company is None:

        raise HTTPException(
            status_code=404,
            detail="Company not found.",
        )

    return company