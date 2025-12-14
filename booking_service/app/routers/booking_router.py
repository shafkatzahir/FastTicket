import json
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user
from fastapi_limiter.depends import RateLimiter
from ..config import settings

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=schemas.BookingRead, status_code=status.HTTP_201_CREATED)
async def book_ticket(
        request: Request,
        booking: schemas.BookingCreate,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user),
        limit: None = Depends(RateLimiter(times=5, minutes=1))
):
    # 1. Prepare the Booking Object
    db_booking = models.Booking(
        user_id=int(user.get("sub")),
        event_id=booking.event_id,
        status="PENDING"
    )

    # 2. Add Booking to Session (Do not commit yet!)
    db.add(db_booking)
    db.flush()  # Flush to get the ID for the message

    # 3. Prepare the Outbox Message
    message_payload = {
        "event_id": booking.event_id,
        "booking_id": db_booking.id,
        "user_id": int(user.get("sub")),
        "status": "booked"
    }

    db_outbox = models.Outbox(
        topic=settings.KAFKA_BOOKING_TOPIC,
        payload=json.dumps(message_payload),
        status="PENDING"
    )

    # 4. Add Outbox Message to Session
    db.add(db_outbox)

    # 5. Commit BOTH together (Atomic Transaction)
    # If this fails, neither the booking nor the message exists.
    db.commit()
    db.refresh(db_booking)

    return db_booking