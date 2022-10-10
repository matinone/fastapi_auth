from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.core.security import create_access_token


router = APIRouter(prefix="/login", tags=["login"])


@router.post(
    "/token",
    response_model=schemas.token.Token,
    status_code=status.HTTP_201_CREATED,
    summary="Get a new access token",
    response_description="The access token",
)
def get_access_token(
    db: Session = Depends(dependencies.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
):
    """
    Get an OAuth2 access token to use in future requests as an
    authenticated user.
    """
    user = models.User.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = create_access_token(subject=user.id)
    response = {
        "access_token": access_token,
        "token_type": "bearer",
    }

    return response
