from redis.asyncio import Redis

from app.core.config import settings


class RedisClient:
    def __init__(self) -> None:
        self._redis: Redis | None = None

    async def connect(self) -> None:
        if self._redis is not None:
            return

        self._redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

        await self._redis.ping()

    async def disconnect(self) -> None:
        if self._redis is None:
            return

        await self._redis.close()
        self._redis = None

    @property
    def client(self) -> Redis:
        if self._redis is None:
            raise RuntimeError("Redis has not been initialized.")

        return self._redis


redis_client = RedisClient()