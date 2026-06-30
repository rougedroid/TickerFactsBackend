from contextlib import asynccontextmanager
from app.api.internal import router as internal_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.company import router as company_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import logger
from app.api.auth import router as auth_router
from app.api.filings import router as filings_router
from app.api.companies import router as company_router
from app.api.websocket import router as websocket_router
from app.realtime.finnhub_client import finnhub_client
from app.realtime.redis_client import redis_client
from app.realtime.redis_pubsub import redis_pubsub

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting TraderView Backend")

    # -------------------------
    # Realtime startup
    # -------------------------
    await redis_client.connect()
    await redis_pubsub.start()
    await finnhub_client.start()

    try:
        yield

    finally:
        logger.info("Stopping TraderView Backend")

        # -------------------------
        # Realtime shutdown
        # -------------------------
        await finnhub_client.stop()
        await redis_pubsub.stop()
        await redis_client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/api/v1")
app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    company_router,
    prefix="/api/v1",
)

app.include_router(
    internal_router,
    prefix="/api/v1",
)

app.include_router(
    filings_router,
    prefix="/api/v1",
)

app.include_router(
    company_router,
    prefix="/api/v1",
)