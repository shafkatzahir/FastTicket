import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth_router
from .database import engine
from . import models
from .config import settings

# Set up a logger
logger = logging.getLogger("auth_service")

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Auth Service starting up...")

    # --- Initialize Redis for Rate Limiting ---
    redis_client = None
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
        logger.info("FastAPILimiter initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize FastAPILimiter: {e}")

    yield  # Application runs here

    logger.info("Auth Service shutting down...")
    if redis_client:
        await redis_client.close()

app = FastAPI(
    title="Auth Service API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (good for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth Service"}