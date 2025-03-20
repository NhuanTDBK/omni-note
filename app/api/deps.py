from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.configs import get_config
from app.db.session import SessionLocal
from app.core.security import ALGORITHM

config = get_config()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db() -> Generator:
    """
    Database dependency that creates a new session for each request
    and closes it afterwards
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> str:
    """
    Get current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Here you can add additional user validation if needed
    # For example, check if user exists in database
    # user = get_user(db, user_id)
    # if user is None:
    #     raise credentials_exception

    return user_id
