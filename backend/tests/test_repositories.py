import os
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi.testclient import TestClient
from backend.app.schemas.repository import RepositoryResponse
from backend.app.main import app
from backend.app.services.github.repositories import GitHubRepositoryError

client = TestClient(app)


class TestRepositoriesAPI(unittest.TestCase):

    def test_get_repositories_missing_token(self):
        response = client.get("/repositories")
        self.assertEqual(response.status_code, 401)
        self.assertIn("GitHub access token is required", response.json()["detail"])

    def test_get_repositories_invalid_token(self):
        with patch(
            "backend.app.api.repositories.GitHubRepositoryService.fetch_user_repositories",
            new_callable=AsyncMock,
            side_effect=GitHubRepositoryError("Invalid or expired GitHub access token.", 401),
        ):
            headers = {"Authorization": "Bearer invalid_token"}
            response = client.get("/repositories", headers=headers)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["detail"], "Invalid or expired GitHub access token.")

    def test_get_repositories_success(self):
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
            "backend.app.api.repositories.GitHubRepositoryService.fetch_user_repositories",
            new_callable=AsyncMock,
            return_value=mock_repos,
        ) as mock_fetch:
            headers = {"Authorization": "Bearer valid_github_access_token"}
            response = client.get("/repositories", headers=headers)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(len(data), 2)

            self.assertEqual(data[0]["name"], "Cryptanium")
            self.assertEqual(data[0]["owner"], "venkatesh-99-cbs")
            self.assertTrue(data[0]["private"])
            self.assertEqual(data[0]["language"], "Python")
            self.assertEqual(data[0]["default_branch"], "main")

            mock_fetch.assert_awaited_once_with(access_token="valid_github_access_token")


if __name__ == "__main__":
    unittest.main()
