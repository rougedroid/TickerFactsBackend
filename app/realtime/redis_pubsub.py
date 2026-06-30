import asyncio
import json
from contextlib import suppress

from app.realtime.broadcaster import broadcaster
from app.realtime.constants import RedisChannel
from app.realtime.redis_client import redis_client


class RedisPubSub:
    def __init__(self) -> None:
        self._pubsub = None
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        self._pubsub = redis_client.client.pubsub()

        await self._pubsub.subscribe(
            RedisChannel.PRICE,
            RedisChannel.METRIC,
            RedisChannel.FILING,
        )

        self._task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()

            with suppress(asyncio.CancelledError):
                await self._task

        if self._pubsub:
            await self._pubsub.close()

    async def publish_price(
        self,
        symbol: str,
        price: float,
        volume: float,
        timestamp: int,
    ) -> None:
        payload = {
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "timestamp": timestamp,
        }

        await redis_client.client.publish(
            RedisChannel.PRICE,
            json.dumps(payload),
        )

    async def publish_metric(
        self,
        symbol: str,
        metrics: dict,
    ) -> None:
        payload = {
            "symbol": symbol,
            "metrics": metrics,
        }

        await redis_client.client.publish(
            RedisChannel.METRIC,
            json.dumps(payload),
        )

    async def publish_filing(
        self,
        symbol: str,
        filing_type: str,
        accession_number: str,
        payload: dict,
    ) -> None:
        message = {
            "symbol": symbol,
            "filing_type": filing_type,
            "accession_number": accession_number,
            "payload": payload,
        }

        await redis_client.client.publish(
            RedisChannel.FILING,
            json.dumps(message),
        )

    async def _listen(self) -> None:
        async for message in self._pubsub.listen():
            if message["type"] != "message":
                continue

            channel = message["channel"]
            payload = json.loads(message["data"])

            if channel == RedisChannel.PRICE:
                await broadcaster.broadcast_price(**payload)

            elif channel == RedisChannel.METRIC:
                await broadcaster.broadcast_metric(**payload)

            elif channel == RedisChannel.FILING:
                await broadcaster.broadcast_filing(**payload)


redis_pubsub = RedisPubSub()