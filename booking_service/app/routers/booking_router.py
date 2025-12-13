from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=schemas.BookingRead, status_code=status.HTTP_201_CREATED)
async def book_ticket(
        booking: schemas.BookingCreate,
        db: Session = Depends(get_db),
        user: dict = Depends(get_current_user),  # Must be logged in
        limit: None = Depends(RateLimiter(times=5, minutes=1))  # Strict limiting
):
    # Phase 1 Logic: Direct DB Write (We will upgrade this to Kafka later)

    # 1. Create Booking
    db_booking = models.Booking(
        user_id=int(user.get("sub")),  # Get ID from JWT
        event_id=booking.event_id,
        status="CONFIRMED"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)

    # Note: In Phase 1, we aren't checking if the event exists or has tickets.
    # That requires cross-service communication (HTTP/Kafka), which is Phase 2.

    return db_booking