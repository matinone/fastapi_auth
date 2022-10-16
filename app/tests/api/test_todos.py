import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import ToDo, User
from app.tests.factories import ToDoFactory


@pytest.mark.parametrize("todo_params", ["title_desc", "no_title", "no_desc"])
def test_create_todo(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    todo_params,
):
    headers, user = auth_headers

    data = {"title": "My first ToDo", "description": "This is just my first ToDo"}

    if todo_params == "no_title":
        data.pop("title")
    elif todo_params == "no_desc":
        data.pop("description")

    response = client.post(
        "/api/todos",
        json=data,
        headers=headers,
    )

    if todo_params == "no_title":
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        assert response.status_code == status.HTTP_201_CREATED

        created_todo = response.json()
        db_todo = ToDo.get_by_id(db_session, id=created_todo["id"])

        assert db_todo
        assert db_todo.user_id == user.id
        assert created_todo["user_id"] == user.id
        assert created_todo["title"] == data["title"]
        assert db_todo.title == data["title"]
        if todo_params == "no_desc":
            assert not created_todo["description"]
            assert not db_todo.description
        else:
            assert created_todo["description"] == data["description"]
            assert db_todo.description == data["description"]


def test_create_todo_not_logged_in(
    client: TestClient,
    db_session: Session,
):
    data = {"title": "My first ToDo", "description": "This is just my first ToDo"}

    response = client.post("/api/todos", json=data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "n_todos", [0, 1, 4], ids=["no_todos", "single_todo", "multiple_todos"]
)
def test_get_todos(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    n_todos,
):
    headers, user = auth_headers

    ToDoFactory.create_batch(n_todos, user=user)

    response = client.get(
        "/api/todos",
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    todos = response.json()
    assert len(todos) == n_todos

    for todo in todos:
        assert "title" in todo
        assert "description" in todo
        assert todo.get("user_id") == user.id


@pytest.mark.parametrize("cases", ["found", "not_found", "other_user"])
def test_get_todo_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    cases,
):
    headers, user = auth_headers

    if cases == "found":
        existing_todo = ToDoFactory.create(user=user)
        todo_id = existing_todo.id
    elif cases == "other_user":
        existing_todo = ToDoFactory.create(user__id=user.id + 1)
        todo_id = existing_todo.id
    else:
        existing_todo = None
        todo_id = 100

    response = client.get(
        f"/api/todos/{todo_id}",
        headers=headers,
    )

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "ToDo not found"}
    elif cases == "other_user":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "ToDo does not belong to current user"}
    elif cases == "found":
        assert response.status_code == status.HTTP_200_OK

        todo = response.json()
        assert todo["id"] == todo_id
        assert todo["title"] == existing_todo.title
        assert todo["description"] == existing_todo.description


@pytest.mark.parametrize("cases", ["found", "not_found", "other_user"])
def test_update_todo_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    cases,
):
    headers, user = auth_headers

    update_data = {"title": "Other Title", "description": "Other description"}

    if cases == "found":
        existing_todo = ToDoFactory.create(user=user)
        todo_id = existing_todo.id
    elif cases == "other_user":
        existing_todo = ToDoFactory.create(user__id=user.id + 1)
        todo_id = existing_todo.id
    else:
        existing_todo = None
        todo_id = 100

    response = client.put(
        f"/api/todos/{todo_id}",
        json=update_data,
        headers=headers,
    )

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "ToDo not found"}
    elif cases == "other_user":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "ToDo does not belong to current user"}
    elif cases == "found":
        assert response.status_code == status.HTTP_200_OK

        todo = response.json()
        assert todo["id"] == todo_id
        assert todo["title"] == update_data["title"]
        assert todo["description"] == update_data["description"]


@pytest.mark.parametrize("cases", ["found", "not_found", "other_user"])
def test_delete_todo_by_id(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    cases,
):
    headers, user = auth_headers

    update_data = {"title": "Other Title", "description": "Other description"}

    if cases == "found":
        existing_todo = ToDoFactory.create(user=user)
        todo_id = existing_todo.id
    elif cases == "other_user":
        existing_todo = ToDoFactory.create(user__id=user.id + 1)
        todo_id = existing_todo.id
    else:
        existing_todo = None
        todo_id = 100

    response = client.delete(
        f"/api/todos/{todo_id}",
        json=update_data,
        headers=headers,
    )

    db_todo = ToDo.get_by_id(db_session, id=todo_id)

    if cases == "not_found":
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "ToDo not found"}
    elif cases == "other_user":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "ToDo does not belong to current user"}
        assert db_todo
    elif cases == "found":
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not db_todo
