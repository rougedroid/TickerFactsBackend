from datetime import datetime
from app.schemas.metric import MetricCreate
from pydantic import BaseModel, ConfigDict


class FilingCreate(BaseModel):

    accession_number: str

    cik: str

    form_type: str

    filer_type: str | None = None

    filing_time: datetime

    processed_info: dict | None = None

    filing_url: str

    metrics: list[MetricCreate] = []


class FilingResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    accession_number: str

    cik: str

    form_type: str

    filer_type: str | None

    filing_time: datetime

    processed_info: dict | None

    filing_url: str