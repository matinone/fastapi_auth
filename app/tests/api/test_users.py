from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.tests.factories import UserFactory


@pytest.mark.parametrize("cases", ["unauthenticated", "not_superuser", "superuser"])
def test_create_user(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    cases: str,
):
    headers, user = auth_headers

    time_before = datetime.utcnow().replace(microsecond=0)
    data = {
        "email": "new_user@example.com",
        "password": "123456",
        "full_name": "Random Name",
    }

    if cases == "unauthenticated":
        response = client.post("/api/users", json=data)
    else:
        User.update(db_session, user, new={"is_superuser": cases == "superuser"})
        response = client.post("/api/users", json=data, headers=headers)

    db_user = User.get_by_email(db_session, email=data["email"])

    if cases == "unauthenticated":
        assert response.status_code == 401
        assert not db_user
    elif cases == "not_superuser":
        assert response.status_code == 403
        assert not db_user
    else:
        assert response.status_code == status.HTTP_201_CREATED
        assert db_user

        created_user = response.json()

        data.pop("password")
        for field in data.keys():
            # check response and original data match
            assert created_user[field] == data[field]
            # check user in DB and original data match
            assert getattr(db_user, field) == data[field]

        assert db_user.is_active
        assert created_user.get("is_active")

        assert not db_user.is_superuser
        assert not created_user.get("is_superuser")

        assert "time_created" in created_user
        time_after = datetime.utcnow().replace(microsecond=0)
        created_user_datetime = datetime.strptime(
            created_user["time_created"], "%Y-%m-%dT%H:%M:%S"
        )

        assert (
            db_user.time_created >= time_before and db_user.time_created <= time_after
        )
        assert (
            created_user_datetime >= time_before and created_user_datetime <= time_after
        )


def test_create_user_existing_email(
    client: TestClient,
    db_session: Session,
    auth_headers_superuser: tuple[dict[str, str], User],
):
    headers, user = auth_headers_superuser

    data = {"email": user.email, "password": "123456"}
    response = client.post("/api/users", json=data, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Email already registered"}


def test_get_user_me(client: TestClient, auth_headers: tuple[dict[str, str], User]):
    headers, user = auth_headers
    response = client.get("/api/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    current_user = response.json()
    assert current_user["email"] == user.email
    assert current_user["full_name"] == user.full_name
    assert current_user["id"] == user.id
    assert current_user["is_active"]
    assert "is_verified" in current_user


@pytest.mark.parametrize(
    "user_type",
    ["user_not_found", "same_user", "other_user_not_super", "other_user_super"],
)
def test_get_user_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    user_type: str,
):
    headers, user = auth_headers

    other_user = None
    if user_type == "user_not_found":
        user_id = "123456789"
    elif user_type == "same_user":
        user_id = user.id
    else:
        other_user = UserFactory.create()
        user_id = other_user.id
        if user_type == "other_user_super":
            user.is_superuser = True
            User.update(db_session, user, new={"is_superuser": True})

    response = client.get(f"/api/users/{user_id}", headers=headers)

    if user_type == "user_not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}
    elif user_type == "other_user_not_super":
        assert response.status_code == status.HTTP_403_FORBIDDEN
    else:
        assert response.status_code == status.HTTP_200_OK
        expected_user = user if user_type == "same_user" else other_user

        resp_user = response.json()
        assert resp_user["email"] == expected_user.email
        assert resp_user["full_name"] == expected_user.full_name
        assert resp_user["id"] == expected_user.id
        assert resp_user["is_active"]
        assert "is_verified" in resp_user


def test_get_users(
    client: TestClient, auth_headers_superuser: tuple[dict[str, str], User]
):
    extra_users = 3
    UserFactory.create_batch(extra_users)

    headers, user = auth_headers_superuser
    response = client.get("/api/users", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    users = response.json()
    assert len(users) == extra_users + 1
    for u in users:
        assert "email" in u
        assert "full_name" in u
        assert "id" in u
        assert u.get("is_active")
        assert "is_verified" in u

    # current user must be present in the returned users list
    assert user.email in [u["email"] for u in users]


def test_update_user_me(
    client: TestClient, db_session: Session, auth_headers: tuple[dict[str, str], User]
):
    headers, user = auth_headers

    update_data = {"full_name": "Other Name"}
    response = client.put("/api/users/me", headers=headers, json=update_data)

    assert response.status_code == status.HTTP_200_OK

    updated_user = response.json()
    db_user = User.get_by_email(db_session, email=user.email)

    assert updated_user["full_name"] == update_data["full_name"]
    assert db_user.full_name == update_data["full_name"]


@pytest.mark.parametrize("found", [True, False], ids=["user_found", "user_not_found"])
def test_update_user_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    found,
):
    headers, user = auth_headers
    user_id = user.id if found else "123456789"
    update_data = {"full_name": "Other Name", "password": "unsecure"}
    response = client.put(f"/api/users/{user_id}", headers=headers, json=update_data)

    if not found:
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}
    else:
        assert response.status_code == status.HTTP_200_OK

        updated_user = response.json()
        db_user = User.get_by_id(db_session, id=user_id)

        assert updated_user["full_name"] == update_data["full_name"]
        assert db_user.full_name == update_data["full_name"]


def test_delete_user_me(
    client: TestClient, db_session: Session, auth_headers: tuple[dict[str, str], User]
):
    headers, user = auth_headers
    current_email = user.email
    response = client.delete("/api/users/me", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_user = User.get_by_email(db_session, email=current_email)
    assert not db_user


@pytest.mark.parametrize("found", [True, False], ids=["user_found", "user_not_found"])
def test_delete_user_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    found,
):
    headers, user = auth_headers
    user_id = user.id if found else "123456789"

    response = client.delete(f"/api/users/{user_id}", headers=headers)

    if not found:
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "User not found"}
    else:
        assert response.status_code == status.HTTP_204_NO_CONTENT

        db_user = User.get_by_id(db_session, id=user_id)
        assert not db_user
