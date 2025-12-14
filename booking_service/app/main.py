import logging
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from aiokafka import AIOKafkaProducer
from sqlalchemy.orm import Session  # Needed for the relay

from .database import engine, SessionLocal  # Need SessionLocal for manual DB access
from . import models
from .routers import booking_router
from .config import settings
from .kafka_consumer import consume_confirmations

logger = logging.getLogger("booking_service")

# Create tables
models.Base.metadata.create_all(bind=engine)


# --- BACKGROUND TASK: THE OUTBOX RELAY ---
async def outbox_relay(producer: AIOKafkaProducer):
    """
    Periodically checks the Outbox table for pending messages and sends them to Kafka.
    """
    logger.info("Outbox Relay started.")
    while True:
        try:
            # 1. Create a new DB session
            db: Session = SessionLocal()
            try:
                # 2. Fetch pending messages (limit 10 to avoid overloading)
                messages = db.query(models.Outbox).filter(models.Outbox.status == "PENDING").limit(10).all()

                for msg in messages:
                    try:
                        logger.info(f"Relaying message {msg.id} to topic {msg.topic}")
                        # 3. Send to Kafka
                        await producer.send_and_wait(msg.topic, msg.payload.encode("utf-8"))

                        # 4. Mark as PROCESSED
                        msg.status = "PROCESSED"
                    except Exception as e:
                        logger.error(f"Failed to relay message {msg.id}: {e}")
                        msg.retry_count += 1
                        # Optional: Mark FAILED if retries > 5

                db.commit()
            finally:
                db.close()

        except Exception as e:
            logger.error(f"Outbox Relay crashed: {e}")

        # Sleep for a bit before checking again
        await asyncio.sleep(5)
    # -----------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Booking Service starting up...")

    # Redis Init
    redis_client = None
    try:
        redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis_client)
    except Exception as e:
        logger.error(f"Failed to initialize FastAPILimiter: {e}")

    # Kafka Producer Init
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
    relay_task = None
    try:
        await producer.start()
        logger.info("Kafka Producer started.")

        # START THE RELAY TASK
        relay_task = asyncio.create_task(outbox_relay(producer))

    except Exception as e:
        logger.error(f"Failed to start Kafka Producer: {e}")

    consumer_task = asyncio.create_task(consume_confirmations())

    yield

    logger.info("Booking Service shutting down...")

    # Cancel relay
    if relay_task:
        relay_task.cancel()
        try:
            await relay_task
        except asyncio.CancelledError:
            logger.info("Outbox Relay stopped.")
    consumer_task.cancel()

    if producer:
        await producer.stop()

    if redis_client:
        await redis_client.close()


app = FastAPI(title="Booking Service API", version="1.0.0", lifespan=lifespan)
app.include_router(booking_router.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"}