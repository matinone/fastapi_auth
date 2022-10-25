import pytest

from app.core.config import Settings, get_settings
from app.main import app


def get_settings_override():
    return Settings(EMAIL_ENABLED=True)


@pytest.fixture()
def mock_email(mocker):
    mock = mocker.patch("app.api.emails.email_utils.send_email")
    app.dependency_overrides[get_settings] = get_settings_override
    yield mock
    # remove the dependency override after running the testcase
    del app.dependency_overrides[get_settings]
