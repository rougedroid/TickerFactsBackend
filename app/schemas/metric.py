from pydantic import BaseModel, ConfigDict


class MetricCreate(BaseModel):

    accession_number: str

    metric_name: str

    metric_category: str | None = None

    numeric_value: float | None = None

    text_value: str | None = None

    boolean_value: bool | None = None

    unit: str | None = None

    period: str | None = None


class MetricResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    accession_number: str

    metric_name: str

    metric_category: str | None

    numeric_value: float | None

    text_value: str | None

    boolean_value: bool | None

    unit: str | None

    period: str | None