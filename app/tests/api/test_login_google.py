from authlib.integrations.starlette_client import OAuthError
from fastapi import Response, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.tests.factories import UserFactory


def mock_oauth_google(
    email="user@example.com", raise_exception=False, return_user_info=True
):
    class FakeGoogleOAuth:
        def __init__(
            self, email="user@example.com", raise_exception=False, return_user_info=True
        ):
            self.email = email
            self.raise_exception = raise_exception
            self.return_user_info = return_user_info

        async def authorize_redirect(self, request, uri):
            return Response(status_code=status.HTTP_302_FOUND)

        async def authorize_access_token(self, request):
            if self.raise_exception:
                raise OAuthError()

            if self.return_user_info:
                return {"userinfo": {"email": self.email}}

            return {}

    class FakeOAuth:
        def __init__(
            self, email="user@example.com", raise_exception=False, return_user_info=True
        ):
            self.google = FakeGoogleOAuth(
                email=email,
                raise_exception=raise_exception,
                return_user_info=return_user_info,
            )

    return FakeOAuth(
        email=email, raise_exception=raise_exception, return_user_info=return_user_info
    )


def test_login_google_redirect(
    client: TestClient,
    db_session: Session,
    mocker,
):

    mocker.patch("app.api.endpoints.login.oauth", mock_oauth_google())

    response = client.get("/api/login_google")
    assert response.status_code == status.HTTP_302_FOUND


def test_login_google_valid_token(
    client: TestClient,
    db_session: Session,
    mocker,
):

    user = UserFactory.create()
    mocker.patch("app.api.endpoints.login.oauth", mock_oauth_google(email=user.email))

    response = client.get("/api/token_google")
    assert response.status_code == status.HTTP_200_OK

    token = response.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"


def test_login_google_oauth_error(
    client: TestClient,
    db_session: Session,
    mocker,
):

    mocker.patch(
        "app.api.endpoints.login.oauth", mock_oauth_google(raise_exception=True)
    )

    response = client.get("/api/token_google")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_login_google_no_user_data(
    client: TestClient,
    db_session: Session,
    mocker,
):

    mocker.patch(
        "app.api.endpoints.login.oauth", mock_oauth_google(return_user_info=False)
    )

    response = client.get("/api/token_google")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Incorrect email or password"}
