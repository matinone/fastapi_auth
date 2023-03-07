from datetime import datetime, timedelta

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

    time_before = datetime.utcnow().replace(microsecond=0)
    data = {"title": "My first ToDo", "description": "This is just my first ToDo"}

    if todo_params == "no_title":
        data.pop("title")
    elif todo_params == "no_desc":
        data.pop("description")

    response = client.post("/api/todos", json=data, headers=headers)

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
        assert not created_todo["done"]
        assert not db_todo.done
        assert not created_todo["time_done"]
        assert not db_todo.time_done
        if todo_params == "no_desc":
            assert not created_todo["description"]
            assert not db_todo.description
        else:
            assert created_todo["description"] == data["description"]
            assert db_todo.description == data["description"]

        assert "time_created" in created_todo
        time_after = datetime.utcnow().replace(microsecond=0)
        created_todo_datetime = datetime.strptime(
            created_todo["time_created"], "%Y-%m-%dT%H:%M:%S"
        )

        assert (
            db_todo.time_created >= time_before and db_todo.time_created <= time_after
        )
        assert (
            created_todo_datetime >= time_before and created_todo_datetime <= time_after
        )


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

    response = client.get("/api/todos", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    todos = response.json()
    assert len(todos) == n_todos

    for todo in todos:
        assert "title" in todo
        assert "description" in todo
        assert "time_created" in todo
        assert todo.get("user_id") == user.id


@pytest.mark.parametrize(
    "datetime_param",
    ["start_datetime", "end_datetime", "start_end_datetime"],
)
def test_get_todos_datetime(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    datetime_param,
):
    headers, user = auth_headers

    now = datetime.utcnow()

    user_now = ToDoFactory.create(user=user, time_created=now)
    user_before = ToDoFactory.create(user=user, time_created=now - timedelta(hours=2))
    user_later = ToDoFactory.create(user=user, time_created=now + timedelta(hours=2))

    # start time to include now and later only
    start_datetime = (now - timedelta(hours=1)).isoformat()
    # end time to include now and before only
    end_datetime = (now + timedelta(hours=1)).isoformat()

    if datetime_param == "start_datetime":
        query_params = f"?start_datetime={start_datetime}"
    elif datetime_param == "end_datetime":
        query_params = f"?end_datetime={end_datetime}"
    else:
        query_params = f"?start_datetime={start_datetime}&end_datetime={end_datetime}"

    response = client.get(
        f"/api/todos{query_params}",
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    todos = response.json()
    if datetime_param == "start_datetime":
        assert len(todos) == 2
        expected_datetimes = [
            user_now.time_created.isoformat(),
            user_later.time_created.isoformat(),
        ]
    elif datetime_param == "end_datetime":
        expected_datetimes = [
            user_now.time_created.isoformat(),
            user_before.time_created.isoformat(),
        ]
        assert len(todos) == 2
    else:
        assert len(todos) == 1
        expected_datetimes = [user_now.time_created.isoformat()]

    for todo in todos:
        assert "title" in todo
        assert "description" in todo
        assert todo.get("user_id") == user.id
        assert todo["time_created"] in expected_datetimes


@pytest.mark.parametrize(
    "done",
    [True, False],
    ids=["done", "not_done"],
)
def test_get_todos_done(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
    done,
):
    headers, user = auth_headers

    done_todos = 5
    not_done_todos = 7
    ToDoFactory.create_batch(done_todos, user=user, done=True)
    ToDoFactory.create_batch(not_done_todos, user=user, done=False)

    response = client.get(f"/api/todos?done={done}", headers=headers)

    assert response.status_code == status.HTTP_200_OK

    todos = response.json()
    assert len(todos) == (done_todos if done else not_done_todos)

    for todo in todos:
        assert "title" in todo
        assert "description" in todo
        assert "time_created" in todo
        assert todo.get("user_id") == user.id
        assert todo["done"] == done


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


def test_delete_user_deletes_todo(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
):
    headers, user = auth_headers
    existing_todo = ToDoFactory.create(user=user)
    todo_id = existing_todo.id

    response = client.delete("/api/users/me", headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_todo = ToDo.get_by_id(db_session, id=todo_id)
    assert not db_todo


def test_mark_as_done(
    client: TestClient,
    db_session: Session,
    auth_headers: tuple[dict[str, str], User],
):
    headers, user = auth_headers

    existing_todo = ToDoFactory.create(user=user)
    todo_id = existing_todo.id

    time_before = datetime.utcnow().replace(microsecond=0)
    response = client.put(
        f"/api/todos/{todo_id}/resolve",
        headers=headers,
    )

    assert response.status_code == status.HTTP_200_OK

    todo = response.json()
    assert todo["id"] == todo_id
    assert todo["done"]

    done_datetime = datetime.strptime(todo["time_done"], "%Y-%m-%dT%H:%M:%S")
    assert done_datetime >= time_before
