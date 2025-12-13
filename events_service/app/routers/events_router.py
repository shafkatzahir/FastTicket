from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..auth import get_current_user # Reused from Auth service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=schemas.EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user), # Requires Login
    limit: None = Depends(RateLimiter(times=10, minutes=1))
):
    # Check if user is admin (Optional logic for later)
    # For now, any logged-in user can create an event
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[schemas.EventRead])
async def list_events(
    skip: int = 0,
    limit_num: int = 100,
    db: Session = Depends(get_db),
    limit: None = Depends(RateLimiter(times=100, minutes=1))
):
    events = db.query(models.Event).offset(skip).limit(limit_num).all()
    return events