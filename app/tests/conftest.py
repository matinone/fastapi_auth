import pytest

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database.db import Base, create_engine_and_session
from app.api.dependencies import get_db
from app.core.security import create_access_token
from app.models import User
from app.tests.factories import UserFactory

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
    connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection) -> Session:
    """
    Fixture to create a new separate transaction for each testcase,
    rolling back all the DB changes after the test finishes.
    This ensures that each testcase starts with an empty DB.
    """
    transaction = db_connection.begin()
    session = TestSessionLocal(bind=db_connection)
    UserFactory._meta.sqlalchemy_session = session

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

    with TestClient(app) as c:
        yield c

    # del app.dependency_overrides[get_db]


@pytest.fixture(scope="function")
def auth_headers(db_session) -> tuple[dict[str, str], User]:
    """
    Fixture to get valid authentication headers for a random user.
    """
    user = UserFactory(email="user@example.com")
    auth_token = create_access_token(subject=user.id)

    headers = {"Authorization": f"Bearer {auth_token}"}
    # return the user as well, in case the test needs it
    return headers, user
