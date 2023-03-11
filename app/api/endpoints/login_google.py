import secrets
import string

import requests
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies

from .login import _check_active_user_exists, _generate_token_response

router = APIRouter(prefix="", tags=["login"])


def _validate_google_token(token: str) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
    )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return resp.json()


@router.post(
    "/token_google",
    response_model=schemas.Token,
    summary="Validate Google token and get a new API access token",
    response_description="The access token",
)
def get_access_token_from_google(
    access_token: str = Body(embed=True),
    db: Session = Depends(dependencies.get_db),
):
    """
    Get an OAuth2 access token from a user logging with Google,
    to use in future requests as an authenticated user.
    """
    user_data = _validate_google_token(access_token)
    user = models.User.get_by_email(db, email=user_data.get("email"))
    _check_active_user_exists(user)

    response = _generate_token_response(user.id)
    return response


@router.post(
    "/register_google",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Validate Google token and create a new user",
    response_description="The created user",
)
def create_user_from_google(
    access_token: str = Body(embed=True),
    db: Session = Depends(dependencies.get_db),
):
    user_data = _validate_google_token(access_token)
    user = models.User.get_by_email(db, email=user_data.get("email"))
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    random_password = "".join(
        secrets.choice(string.ascii_letters + string.digits) for i in range(20)
    )
    user_create = schemas.UserCreate(email=user_data["email"], password=random_password)
    if "name" in user_data:
        user_create.full_name = user_data["name"]

    # user already verified if registering using Google
    user = models.User.create(db, user_create, is_verified=True)

    return user
