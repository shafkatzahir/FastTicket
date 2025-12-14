import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import events_router
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from .config import settings

# --- NEW IMPORT ---
from .kafka_consumer import consume_booking_events

logger = logging.getLogger("events_service")

# Create tables
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Events Service starting up...")

    # 1. Start Redis
    redis_client = None
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
    except Exception as e:
        logger.error(f"Failed to initialize FastAPILimiter: {e}")

    # 2. Start Kafka Consumer (Background Task) --- NEW SECTION ---
    consumer_task = asyncio.create_task(consume_booking_events())
    logger.info("Kafka Consumer task initiated.")
    # -----------------------------------------------------------

    yield

    logger.info("Events Service shutting down...")

    # 3. Graceful Shutdown --- NEW SECTION ---
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        logger.info("Kafka Consumer task cancelled.")
    # ----------------------------------------

    if redis_client:
        await redis_client.close()


app = FastAPI(title="Events Service API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Events Service"}