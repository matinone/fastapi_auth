import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.tests.factories import UserFactory


def mock_validate_google_token(token: str):
    if token not in ["valid", "no_user", "already_registered"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )

    return {"email": "user@example.com", "name": "User Example"}


@pytest.mark.parametrize("token", ["valid", "invalid", "no_user"])
def test_login_google_token(
    client: TestClient,
    db_session: Session,
    mocker,
    token: str,
):
    if token != "no_user":
        UserFactory.create(email="user@example.com")

    mocker.patch(
        "app.api.endpoints.login_google._validate_google_token",
        mock_validate_google_token,
    )

    response = client.post("/api/token_google", json={"access_token": token})

    if token == "valid":
        assert response.status_code == status.HTTP_200_OK

        token = response.json()
        assert "access_token" in token
        assert token["token_type"] == "bearer"
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("token", ["valid", "invalid", "already_registered"])
def test_register_google(
    client: TestClient,
    db_session: Session,
    mocker,
    token: str,
):

    email = "user@example.com"
    mocker.patch(
        "app.api.endpoints.login_google._validate_google_token",
        mock_validate_google_token,
    )

    if token == "already_registered":
        UserFactory.create(email=email)

    response = client.post("/api/register_google", json={"access_token": token})

    if token == "valid":
        assert response.status_code == status.HTTP_201_CREATED

        db_user = User.get_by_email(db_session, email=email)
        assert db_user
        assert db_user.email == email
        assert db_user.is_verified
    else:
        assert response.status_code == status.HTTP_400_BAD_REQUEST
