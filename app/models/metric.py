from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    Double,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Metric(Base):

    __tablename__ = "metrics"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    accession_number: Mapped[str] = mapped_column(
        ForeignKey("filings.accession_number"),
        nullable=False,
        index=True,
    )

    metric_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    metric_category: Mapped[str | None] = mapped_column(
        String(100),
    )

    numeric_value: Mapped[float | None] = mapped_column(
        Double,
    )

    text_value: Mapped[str | None] = mapped_column(
        Text,
    )

    boolean_value: Mapped[bool | None] = mapped_column(
        Boolean,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
    )

    period: Mapped[str | None] = mapped_column(
        String(30),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    filing = relationship(
        "Filing",
        back_populates="metrics",
    )