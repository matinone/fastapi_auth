import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import create_access_token
from app.database.db import Base, create_engine_and_session
from app.main import app, google_auth_app
from app.models import User
from app.tests.factories import UserFactory, factory_list

test_engine, TestSessionLocal = create_engine_and_session(
    db_url="sqlite:///./sql_test.db"
)

# create the test database
# (this is also called in main.py but with a different database)
Base.metadata.create_all(bind=test_engine)


@pytest.fixture(scope="session")
def db_connection():
    """
    Fixture to use a single DB connection for the whole testsuite.
    """
    connection = test_engine.connect()
    yield connection

    # get path to delete SQLite DB file
    db_path = ""
    for id_number, name, file_name in connection.execute("PRAGMA database_list"):
        if name == "main" and file_name is not None:
            db_path = file_name
            break

    connection.close()

    try:
        print("Removing database file")
        os.remove(db_path)
    except FileNotFoundError:
        print("Database file not found")


@pytest.fixture(scope="function")
def db_session(db_connection) -> Session:
    """
    Fixture to create a new separate transaction for each testcase,
    rolling back all the DB changes after the test finishes.
    This ensures that each testcase starts with an empty DB.
    """
    transaction = db_connection.begin()
    session = TestSessionLocal(bind=db_connection)

    for fact in factory_list:
        fact._meta.sqlalchemy_session = session

    yield session

    session.close()
    transaction.rollback()


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    # override get_db dependency to return the DB session from the fixture
    # (instead of creating a new one)
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    google_auth_app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # del app.dependency_overrides[get_db]


@pytest.fixture(scope="function")
def auth_headers(db_session) -> tuple[dict[str, str], User]:
    """
    Fixture to get valid authentication headers for an example user.
    """
    user = UserFactory.create(email="user@example.com")
    auth_token = create_access_token(subject=user.id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    # return the user as well, in case the test needs it
    return headers, user


@pytest.fixture(scope="function")
def auth_headers_superuser(db_session, auth_headers) -> tuple[dict[str, str], User]:
    """
    Fixture to get valid authentication headers for a superuser.
    """
    headers, user = auth_headers
    User.update(db_session, user, new={"is_superuser": True})

    # return the user as well, in case the test needs it
    return headers, user
