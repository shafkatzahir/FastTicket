from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLEnum
from enum import Enum as PyEnum
from app.database import Base

class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    refresh_token_hash = Column(String, nullable=True)