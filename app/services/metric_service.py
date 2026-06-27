from app.models.metric import Metric
from app.repositories.metric_repository import MetricRepository


class MetricService:

    def __init__(self, db):

        self.repo = MetricRepository(db)

    async def ingest(
        self,
        metrics,
    ):

        objects = []

        for metric in metrics:

            objects.append(
                Metric(
                    accession_number=metric.accession_number,
                    metric_name=metric.metric_name,
                    metric_category=metric.metric_category,
                    numeric_value=metric.numeric_value,
                    text_value=metric.text_value,
                    boolean_value=metric.boolean_value,
                    unit=metric.unit,
                    period=metric.period,
                )
            )

        await self.repo.bulk_create(objects)

    async def filing_metrics(
        self,
        accession_number: str,
    ):

        return await self.repo.get_by_accession(
            accession_number
        )