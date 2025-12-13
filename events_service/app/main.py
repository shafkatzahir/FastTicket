import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine
from . import models
from .routers import events_router # Import the correct router
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("events_service")

# Create tables in events_db
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Events Service starting up...")
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8")
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize FastAPILimiter: {e}")

    yield

    logger.info("Events Service shutting down...")
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