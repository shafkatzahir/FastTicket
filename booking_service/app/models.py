from sqlalchemy import Column, Integer, String, DateTime,Text
from sqlalchemy.sql import func
from .database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    event_id = Column(Integer, nullable=False)
    status = Column(String, default="CONFIRMED")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    payload = Column(Text, nullable=False)  # Stores the JSON message
    status = Column(String, default="PENDING")  # PENDING, PROCESSED, FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    retry_count = Column(Integer, default=0)