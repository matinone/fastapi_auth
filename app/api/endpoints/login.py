from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.api.emails.email_utils import send_account_verification_email
from app.core.config import Settings, get_settings
from app.core.security import (create_access_token,
                               create_account_verification_token,
                               create_refresh_token, decode_token)

router = APIRouter(prefix="", tags=["login"])


def _check_active_user_exists(user):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )


def _generate_token_response(user_id, include_refresh=True):
    response = {
        "access_token": create_access_token(subject=user_id),
        "token_type": "bearer",
    }

    if include_refresh:
        response["refresh_token"] = create_refresh_token(subject=user_id)

    return response


@router.post(
    "/token",
    response_model=schemas.Token,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    summary="Get a new access token",
    response_description="The access token",
)
def get_access_token_from_username(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
):
    """
    Get an OAuth2 access token from a user logging in with a username and password,
    to use in future requests as an authenticated user.
    """
    user = models.User.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    _check_active_user_exists(user)

    response = _generate_token_response(user.id)
    return response


@router.post(
    "/refresh_token",
    response_model=schemas.Token,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
    summary="Get a new access token from a refresh token",
    response_description="The access token",
)
def get_access_token_from_refresh_token(
    refresh_token: schemas.RefreshToken,
    db: Session = Depends(dependencies.get_db),
    settings: Settings = Depends(get_settings),
):
    if refresh_token.grant_type != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )

    token_data = dependencies.decode_token(refresh_token.token, settings)
    user = models.User.get_by_id(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    response = _generate_token_response(user.id, include_refresh=False)
    return response


@router.post(
    "/register",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="The new created user",
)
def register_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
    settings: Settings = Depends(get_settings),
    request: Request,
):
    user = models.User.get_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # already verified if emails are not supported
    is_verified = not settings.EMAIL_ENABLED
    user = models.User.create(db, user_in, is_verified)

    if settings.EMAIL_ENABLED:
        # send account verification email
        account_verification_token = create_account_verification_token(user.email)
        endpoint = request.url_for("verify_account")
        account_verification_url = f"{endpoint}?token={account_verification_token}"
        send_account_verification_email(user, account_verification_url)

    return user


@router.post(
    "/verify_account",
    summary="Account verification",
)
def verify_account(
    token: str = Body(..., embed=True),
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

    models.User.update(db, current=user, new={"is_verified": True})

    return {"message": "User verified"}
