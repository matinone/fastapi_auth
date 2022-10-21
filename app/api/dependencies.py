from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import Settings, get_settings
from app.database.db import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login/token")


def decode_token(token: str, settings: Settings) -> schemas.TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # raises ValidationError if the payload is not valid
        token_data = schemas.TokenPayload(**payload)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token expired",
        )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def get_db():
    """
    Dependency to create/close a new session per request,
    making sure that the session is always closed even if
    there is an exception.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> models.User:
    """
    Dependency to get the current user from the provided token.
    """
    token_data = decode_token(token, settings)
    user = models.User.get_by_id(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return current_user
