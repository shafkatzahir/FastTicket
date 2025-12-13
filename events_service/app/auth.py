# FastTicket/events_service/app/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/auth/login") # Point to Auth Service

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Stateless validation. Decodes JWT and returns payload.
    Does NOT query the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode token using the shared SECRET_KEY
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception
        # Return a simple dict instead of a DB model
        return {"id": user_id, "role": role, "sub": str(user_id)}
    except JWTError:
        raise credentials_exception