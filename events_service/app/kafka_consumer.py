import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from .database import SessionLocal
from .config import settings
from . import crud

logger = logging.getLogger("events_consumer")


async def consume_booking_events():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_BOOKING_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="events_service_group",
        auto_offset_reset="earliest"
    )
    producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)

    await consumer.start()
    await producer.start()
    logger.info("Events Consumer & Producer started.")

    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
                event_id = payload.get("event_id")
                booking_id = payload.get("booking_id")
                status = payload.get("status")

                if status == "booked" and event_id:
                    db = SessionLocal()
                    try:
                        # 1. Attempt Reservation
                        result = crud.reserve_ticket(db, event_id)

                        logger.info(f"Reservation result for Booking {booking_id}: {result}")

                        # 2. Determine Reply Status
                        reply_status = "CONFIRMED" if result == "CONFIRMED" else "REJECTED"

                        # 3. Send Reply
                        reply_message = {
                            "booking_id": booking_id,
                            "status": reply_status,
                            "reason": result  # Send "SOLD_OUT" or "NOT_FOUND" as metadata
                        }

                        await producer.send_and_wait(
                            settings.KAFKA_CONFIRMATION_TOPIC,
                            json.dumps(reply_message).encode("utf-8")
                        )

                    finally:
                        db.close()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    finally:
        await consumer.stop()
        await producer.stop()