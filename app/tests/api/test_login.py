import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User


def test_get_token_valid(
    client: TestClient, db_session: Session,
):
    user_data = {"email": "test@test.com", "password": "123456"}

    response = client.post("/api/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    form_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("api/login/token", data=form_data)

    assert response.status_code == status.HTTP_201_CREATED

    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"


@pytest.mark.parametrize("cases", ["incorrect", "inactive"])
def test_get_token_invalid(
    client: TestClient, db_session: Session, cases: str,
):
    user_data = {"email": "test@test.com", "password": "123456"}

    response = client.post("/api/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    form_data = {"username": user_data["email"], "password": user_data["password"]}
    if cases == "incorrect":
        form_data["password"] = "wrong_password"
    else:
        db_user = User.get_by_email(db_session, email=user_data["email"])
        db_user.is_active = False

    response = client.post("api/login/token", data=form_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    if cases == "incorrect":
        assert response.json() == {"detail": "Incorrect email or password"}
    else:
        assert response.json() == {"detail": "Inactive user"}


def test_current_user_invalid(
    client: TestClient, db_session: Session
):
    auth_token = "invalid_token_string"
    headers = {"Authorization": f"Bearer {auth_token}"}

    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Could not validate credentials"}


def test_current_user_non_existent(
    client: TestClient, db_session: Session,
    auth_headers: tuple[dict[str, str], User],
):
    headers, user = auth_headers

    User.delete(db_session, user=user)

    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_current_user_inactive(
    client: TestClient, db_session: Session,
    auth_headers: tuple[dict[str, str], User],
):
    headers, user = auth_headers

    User.update(db_session, current=user, new={"is_active": False})

    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Inactive user"}
