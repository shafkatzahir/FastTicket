import json
import logging
from aiokafka import AIOKafkaConsumer
from .database import SessionLocal
from .config import settings
from . import crud

logger = logging.getLogger("booking_consumer")


async def consume_confirmations():
    """
    Listens for confirmations from Events Service and updates Booking DB.
    """
    consumer = AIOKafkaConsumer(
        settings.KAFKA_CONFIRMATION_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="booking_service_group",
        auto_offset_reset="earliest"
    )

    await consumer.start()
    logger.info("Booking Confirmation Consumer started.")

    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))
                booking_id = data.get("booking_id")
                status = data.get("status")

                if booking_id and status:
                    logger.info(f"Received confirmation for Booking {booking_id}: {status}")

                    db = SessionLocal()
                    try:
                        crud.update_booking_status(db, booking_id, status)
                    finally:
                        db.close()

            except Exception as e:
                logger.error(f"Error processing confirmation: {e}")
    finally:
        await consumer.stop()