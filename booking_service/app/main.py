import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

from .database import engine
from . import models
from .routers import booking_router
from .config import settings

# Setup logger
logger = logging.getLogger("booking_service")

# Create database tables (bookings table)
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    logger.info("Booking Service starting up...")

    # --- Initialize Redis for Rate Limiting ---
    # We use the REDIS_URL from settings (injected by Docker)
    redis_client = None
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized with Redis.")
    except Exception as e:
        logger.error(f"Failed to initialize FastAPILimiter: {e}")

    yield  # The application runs here

    # --- Shutdown ---
    logger.info("Booking Service shutting down...")
    if redis_client:
        await redis_client.close()

app = FastAPI(
    title="Booking Service API",
    description="Handles ticket bookings.",
    version="1.0.0",
    lifespan=lifespan
)

# Include only the booking router
app.include_router(booking_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"}