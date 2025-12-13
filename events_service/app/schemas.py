from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    price: float
    total_tickets: int
    date: datetime

class EventCreate(EventBase):
    pass

class EventRead(EventBase):
    id: int
    tickets_sold: int
    created_at: datetime

    class Config:
        from_attributes = True