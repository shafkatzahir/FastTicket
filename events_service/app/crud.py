from sqlalchemy.orm import Session
from . import models


def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def reserve_ticket(db: Session, event_id: int) -> str:
    """
    Attempts to reserve a ticket.
    Returns: "CONFIRMED", "SOLD_OUT", or "NOT_FOUND"
    """
    # 1. Lock the row to prevent race conditions (Optional but good for high concurrency)

    event = db.query(models.Event).filter(models.Event.id == event_id).with_for_update().first()

    if not event:
        return "NOT_FOUND"

    # 2. Check Availability
    if event.tickets_sold >= event.total_tickets:
        return "SOLD_OUT"

    # 3. Update
    event.tickets_sold += 1
    db.commit()
    db.refresh(event)
    return "CONFIRMED"