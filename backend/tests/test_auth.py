from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.oauth_state import create_state
from app.core.security import decode_access_token
from app.database.base import Base
from app.database.database import get_db
from app.database.models import User
from app.database.schemas import GitHubUserData
from app.main import app

# Setup test in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


client = TestClient(app, follow_redirects=False)


def test_auth_login_redirect():
    settings.GITHUB_CLIENT_ID = "test_client_id"
    response = client.get("/auth/login")

    assert response.status_code == 307
    redirect_url = response.headers["location"]
    assert "https://github.com/login/oauth/authorize" in redirect_url
    assert "client_id=test_client_id" in redirect_url


def test_auth_callback_missing_code():
    response = client.get("/auth/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Authorization code parameter 'code' is required."


def test_auth_callback_error_param():
    response = client.get("/auth/callback?error=access_denied&error_description=User+cancelled")
    assert response.status_code == 400
    assert response.json()["detail"] == "User cancelled"


def test_auth_callback_success():
    settings.GITHUB_CLIENT_ID = "test_client_id"
    settings.GITHUB_CLIENT_SECRET = "test_client_secret"

    mock_user_data = GitHubUserData(
        id="12345",
        username="octocat",
        email="octocat@github.com",
        avatar_url="https://github.com/images/error/octocat_happy.gif",
    )

    with patch(
        "app.api.auth.GitHubOAuthService.exchange_code_for_token",
        new_callable=AsyncMock,
        return_value="mock_github_access_token",
    ) as mock_exchange, patch(
        "app.api.auth.GitHubOAuthService.fetch_user_profile",
        new_callable=AsyncMock,
        return_value=mock_user_data,
    ) as mock_fetch:

        response = client.get(f"/auth/callback?code=valid_auth_code&state={create_state()}")

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["github_id"] == "12345"
        assert data["user"]["username"] == "octocat"
        assert data["user"]["email"] == "octocat@github.com"
        assert data["user"]["avatar_url"] == "https://github.com/images/error/octocat_happy.gif"

        # Verify JWT payload
        payload = decode_access_token(data["access_token"])
        assert payload is not None
        assert payload["github_id"] == "12345"
        assert payload["username"] == "octocat"

        # Verify database record
        db = TestingSessionLocal()
        user_in_db = db.query(User).filter(User.github_id == "12345").first()
        assert user_in_db is not None
        assert user_in_db.username == "octocat"
        db.close()

        mock_exchange.assert_awaited_once_with("valid_auth_code")
        mock_fetch.assert_awaited_once_with("mock_github_access_token")
