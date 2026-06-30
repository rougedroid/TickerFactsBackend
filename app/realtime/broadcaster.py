from app.realtime.connection_manager import connection_manager
from app.realtime.subscription_manager import subscription_manager
from app.schemas.websocket import (
    FilingUpdateMessage,
    MetricUpdateMessage,
    PriceUpdateMessage,
)


class Broadcaster:
    """
    Broadcasts events to subscribed websocket clients.

    This class is intentionally unaware of:
        - FastAPI routes
        - Finnhub
        - Redis

    It simply sends websocket messages to interested connections.
    """

    async def broadcast_price(
        self,
        symbol: str,
        price: float,
        volume: float,
        timestamp: int,
    ) -> None:
        message = PriceUpdateMessage(
            symbol=symbol,
            price=price,
            volume=volume,
            timestamp=timestamp,
        )

        for connection_id in subscription_manager.get_connections(symbol):
            await connection_manager.send(connection_id, message)

    async def publish_price(
        self,
        symbol: str,
        price: float,
        volume: float,
        timestamp: int,
    ) -> None:
        from app.realtime.redis_pubsub import redis_pubsub

        await redis_pubsub.publish_price(
            symbol=symbol,
            price=price,
            volume=volume,
            timestamp=timestamp,
        )

    async def broadcast_metric(
        self,
        symbol: str,
        metrics: dict,
    ) -> None:
        message = MetricUpdateMessage(
            symbol=symbol,
            metrics=metrics,
        )

        for connection_id in subscription_manager.get_connections(symbol):
            await connection_manager.send(connection_id, message)

    async def publish_metric(
        self,
        symbol: str,
        metrics: dict,
    ) -> None:
        from app.realtime.redis_pubsub import redis_pubsub

        await redis_pubsub.publish_metric(
            symbol=symbol,
            metrics=metrics,
        )

    async def broadcast_filing(
        self,
        symbol: str,
        filing_type: str,
        accession_number: str,
        payload: dict,
    ) -> None:
        message = FilingUpdateMessage(
            symbol=symbol,
            filing_type=filing_type,
            accession_number=accession_number,
            payload=payload,
        )

        for connection_id in subscription_manager.get_connections(symbol):
            await connection_manager.send(connection_id, message)

    async def publish_filing(
        self,
        symbol: str,
        filing_type: str,
        accession_number: str,
        payload: dict,
    ) -> None:
        from app.realtime.redis_pubsub import redis_pubsub

        await redis_pubsub.publish_filing(
            symbol=symbol,
            filing_type=filing_type,
            accession_number=accession_number,
            payload=payload,
        )


broadcaster = Broadcaster()
