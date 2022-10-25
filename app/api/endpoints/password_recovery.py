from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models
from app.api import dependencies
from app.api.emails.email_utils import send_password_recovery_email
from app.core.config import Settings, get_settings
from app.core.security import create_password_reset_token, decode_token

router = APIRouter(prefix="", tags=["password_recovery"])


@router.post(
    "/password_recovery",
    status_code=status.HTTP_201_CREATED,
    summary="Password recovery",
)
def recover_password(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    db: Session = Depends(dependencies.get_db),
    settings: Settings = Depends(get_settings),
):
    if not settings.EMAIL_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sending emails not supported",
        )

    user = models.User.get_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user registered with that email",
        )

    password_reset_token = create_password_reset_token(email)
    endpoint = request.url_for("reset_password")
    reset_url = f"{endpoint}?token={password_reset_token}"
    send_password_recovery_email(user=user, url=reset_url)

    return {"message": "Password recovery email sent"}


@router.post(
    "/password_reset",
    summary="Password reset",
)
def reset_password(
    token: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(dependencies.get_db),
    settings: Settings = Depends(get_settings),
):
    token_data = decode_token(token, settings)
    user = models.User.get_by_email(db, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user registered with that email",
        )

    models.User.update(db, current=user, new={"password": password})

    return {"message": "Password updated"}
