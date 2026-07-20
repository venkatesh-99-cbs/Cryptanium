from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.database.schemas import RepositoryResponse
from app.main import app
from app.services.github.repositories import GitHubRepositoryError

client = TestClient(app)


def test_get_repositories_missing_token():
    response = client.get("/repositories")
    assert response.status_code == 401
    assert "GitHub access token is required" in response.json()["detail"]


def test_get_repositories_invalid_token():
    with patch(
        "app.api.repositories.GitHubRepositoryService.fetch_user_repositories",
        new_callable=AsyncMock,
        side_effect=GitHubRepositoryError("Invalid or expired GitHub access token.", 401),
    ):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/repositories", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired GitHub access token."


def test_get_repositories_success():
    mock_repos = [
        RepositoryResponse(
            name="Cryptanium",
            owner="venkatesh-99-cbs",
            private=True,
            language="Python",
            default_branch="main",
            updated_at="2026-07-20T20:00:00Z",
        ),
        RepositoryResponse(
            name="open-source-tool",
            owner="venkatesh-99-cbs",
            private=False,
            language="TypeScript",
            default_branch="master",
            updated_at="2026-07-19T15:30:00Z",
        ),
    ]

    with patch(
        "app.api.repositories.GitHubRepositoryService.fetch_user_repositories",
        new_callable=AsyncMock,
        return_value=mock_repos,
    ) as mock_fetch:
        headers = {"Authorization": "Bearer valid_github_access_token"}
        response = client.get("/repositories", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        assert data[0]["name"] == "Cryptanium"
        assert data[0]["owner"] == "venkatesh-99-cbs"
        assert data[0]["private"] is True
        assert data[0]["language"] == "Python"
        assert data[0]["default_branch"] == "main"
        assert data[0]["updated_at"] == "2026-07-20T20:00:00Z"

        assert data[1]["name"] == "open-source-tool"
        assert data[1]["owner"] == "venkatesh-99-cbs"
        assert data[1]["private"] is False
        assert data[1]["language"] == "TypeScript"
        assert data[1]["default_branch"] == "master"

        mock_fetch.assert_awaited_once_with(access_token="valid_github_access_token")
