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
    tickets_sold = Column(Integer, default=0, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    @property
    def available_tickets(self):
        return self.total_tickets - self.tickets_sold