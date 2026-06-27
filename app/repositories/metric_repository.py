from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric


class MetricRepository:

    def __init__(self, db: AsyncSession):

        self.db = db

    async def bulk_create(
        self,
        metrics: list[Metric],
    ):

        self.db.add_all(metrics)

        await self.db.commit()

    async def get_by_accession(
        self,
        accession_number: str,
    ):

        result = await self.db.execute(
            select(Metric).where(
                Metric.accession_number == accession_number
            )
        )

        return result.scalars().all()