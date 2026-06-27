from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FilingCreate(BaseModel):

    accession_number: str

    cik: str

    form_type: str

    filer_type: str | None = None

    filing_time: datetime

    processed_info: dict | None = None

    filing_url: str


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