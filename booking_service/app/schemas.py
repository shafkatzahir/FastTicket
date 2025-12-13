from pydantic import BaseModel
from datetime import datetime

class BookingCreate(BaseModel):
    event_id: int

class BookingRead(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True