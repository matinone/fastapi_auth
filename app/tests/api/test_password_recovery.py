from unittest.mock import ANY, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import create_password_reset_token
from app.main import app
from app.models import User
from app.tests.factories import UserFactory


def get_settings_override():
    return Settings(EMAIL_ENABLED=True)


def fake_send_recovery_email(to, subj, body):
    pass


@pytest.fixture()
def mock_email(mocker):
    mock = mocker.patch("app.api.emails.email_utils.send_email")
    app.dependency_overrides[get_settings] = get_settings_override
    yield mock
    # remove the dependency override after running the testcase
    del app.dependency_overrides[get_settings]


def test_send_password_recovery_email(
    client: TestClient,
    db_session: Session,
    mock_email: MagicMock,
):
    user = UserFactory.create()
    response = client.post("api/password_recovery", json={"email": user.email})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Password recovery email sent"}
    mock_email.assert_called_once_with(
        user.email, f"Password Recovery for user {user.email}", ANY
    )


def test_send_password_recovery_email_disabled(
    client: TestClient,
    db_session: Session,
):
    user = UserFactory.create()
    response = client.post("api/password_recovery", json={"email": user.email})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Sending emails not supported"}


def test_send_password_recovery_email_not_found(
    client: TestClient,
    db_session: Session,
    mock_email: MagicMock,
):
    response = client.post("api/password_recovery", json={"email": "user@example.com"})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No user registered with that email"}
    mock_email.assert_not_called()


def test_reset_password(
    client: TestClient,
    db_session: Session,
):
    user = UserFactory.create(hashed_password="dummy_hash")
    previous_hashed_pw = user.hashed_password

    token = create_password_reset_token(user.email)
    new_password = "some_other_password"
    reset_data = {"token": token, "password": new_password}
    response = client.post("api/password_reset", json=reset_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Password updated"}
    assert user.hashed_password != previous_hashed_pw


def test_reset_password_not_found(
    client: TestClient,
    db_session: Session,
):
    user = UserFactory.create(hashed_password="dummy_hash")

    token = create_password_reset_token(user.email)
    new_password = "some_other_password"
    reset_data = {"token": token, "password": new_password}
    User.delete(db_session, user)
    response = client.post("api/password_reset", json=reset_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No user registered with that email"}
