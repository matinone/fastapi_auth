from fastapi import status
from fastapi.testclient import TestClient


def test_register_user_create_todo(client: TestClient):

    # step 1: register a new user
    user_data = {
        "email": "user@example.com",
        "password": "123456",
        "full_name": "Random Name",
    }

    response = client.post("/api/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED

    # step 2: get an access token for the user
    form_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("api/token", data=form_data)
    assert response.status_code == status.HTTP_201_CREATED

    access_token = response.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # step 3: get current user information
    response = client.get("/api/users/me", headers=auth_header)
    assert response.status_code == status.HTTP_200_OK
    current_user = response.json()
    assert current_user["email"] == user_data["email"]
    assert current_user["full_name"] == user_data["full_name"]

    # step 4: create a todo
    todo_data = {"title": "My first ToDo", "description": "This is just my first ToDo"}
    response = client.post("/api/todos", json=todo_data, headers=auth_header)
    assert response.status_code == status.HTTP_201_CREATED

    # step 5: get todos
    response = client.get("/api/todos", headers=auth_header)
    assert response.status_code == status.HTTP_200_OK
    todos = response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == todo_data["title"]
    assert todos[0]["description"] == todo_data["description"]

    # step 6: delete user
    response = client.delete("/api/users/me", headers=auth_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # step 7: check token is no longer valid
    response = client.get("/api/users/me", headers=auth_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # step 8: check it is not possible to get a new token
    form_data = {"username": user_data["email"], "password": user_data["password"]}
    response = client.post("api/token", data=form_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
