from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.filing import FilingResponse
from app.services.filing_service import FilingService

router = APIRouter(
    prefix="/filings",
    tags=["Filings"],
)

@router.get(
    "/latest",
    response_model=list[FilingResponse],
)
async def latest(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):

    service = FilingService(db)

    return await service.latest(limit)

@router.get(
    "/{accession_number}",
    response_model=FilingResponse,
)


async def get_filing(
    accession_number: str,
    db: AsyncSession = Depends(get_db),
):

    service = FilingService(db)

    try:

        return await service.get(
            accession_number
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    
@router.get(
    "/company/{ticker}",
    response_model=list[FilingResponse],
)

async def company_filings(
    ticker: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):

    service = FilingService(db)

    try:

        return await service.company_filings(
            ticker,
            limit,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    

