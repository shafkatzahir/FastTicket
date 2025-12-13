from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    total_tickets = Column(Integer, nullable=False)

    # --- THESE ARE LIKELY MISSING OR NULL ---
    # Schema expects 'tickets_sold', so model MUST have it.
    tickets_sold = Column(Integer, default=0, nullable=False)

    # Schema expects 'created_at', so model MUST have it.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # ----------------------------------------

    date = Column(DateTime(timezone=True), nullable=False)