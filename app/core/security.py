from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.schemas import TokenPayload

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decode_token(token: str, settings: Settings) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # raises ValidationError if the payload is not valid
        token_data = TokenPayload(**payload)
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


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(subject: str | int) -> str:
    expire = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    return create_access_token(subject, expire)


def create_password_reset_token(email: str) -> str:
    expire = timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    return create_access_token(email, expire)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
