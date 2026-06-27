from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Filing(Base):

    __tablename__ = "filings"

    accession_number: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    cik: Mapped[str] = mapped_column(
        ForeignKey("companies.cik"),
        nullable=False,
        index=True,
    )

    form_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    filer_type: Mapped[str | None] = mapped_column(
        String(30),
    )

    filing_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    processed_info: Mapped[dict | None] = mapped_column(
        JSONB,
    )

    filing_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    company = relationship(
        "Company",
        back_populates="filings",
    )