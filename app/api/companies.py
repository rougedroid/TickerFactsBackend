from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.company import CompanyResponse
from app.services.company_service import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)

@router.get(
    "/search",
    response_model=list[CompanyResponse],
)
async def search_companies(
    q: str,
    db: AsyncSession = Depends(get_db),
):

    service = CompanyService(db)

    return await service.search(q)