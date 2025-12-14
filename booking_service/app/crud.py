from sqlalchemy.orm import Session
from . import models

def update_booking_status(db: Session, booking_id: int, status: str):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        booking.status = status
        db.commit()
        db.refresh(booking)
        return booking
    return None