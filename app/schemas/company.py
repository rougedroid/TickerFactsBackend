from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):

    ticker: str
    cik: str
    name: str
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None


class CompanyResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticker: str
    cik: str
    name: str
    exchange: str | None
    sector: str | None
    industry: str | None