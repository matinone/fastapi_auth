from fastapi import status

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.tests.factories import UserFactory

def test_create_user(client: TestClient, db_session: Session):

    data = {"email": "user@example.com",
            "password": "123456",
            "full_name": "Random Name"}

    response = client.post(
        "/api/users", json=data,
    )

    assert response.status_code == status.HTTP_201_CREATED

    created_user = response.json()
    db_user = User.get_by_email(db_session, email=data["email"])

    assert db_user
    data.pop("password")
    for field in data.keys():
        # check response and original data match
        assert created_user[field] == data[field]
        # check user in DB and original data match
        assert getattr(db_user, field) == data[field]

    assert db_user.is_active
    assert created_user.get("is_active")


def test_create_user_existing_email(client: TestClient, db_session: Session):

    user = UserFactory.create()

    data = {"email": user.email,
            "password": "123456"}

    response = client.post(
        "/api/users", json=data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email already registered"}
