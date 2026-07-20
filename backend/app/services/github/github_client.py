from typing import Any
import httpx


class GitHubClientError(Exception):
    """Exception raised when calls to GitHub API fail."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GitHubClient:
    """HTTP client for GitHub REST API using httpx."""

    BASE_URL = "https://api.github.com"

    async def get_user_repositories(
        self, access_token: str, visibility: str = "all", per_page: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch repositories for the authenticated GitHub user."""
        if not access_token or not access_token.strip():
            raise GitHubClientError("GitHub access token is required.", 401)

        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Cryptanium-App",
        }
        params = {"visibility": visibility, "per_page": per_page, "sort": "updated"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/user/repos", headers=headers, params=params
                )
            except httpx.RequestError as exc:
                raise GitHubClientError(f"Network error connecting to GitHub API: {str(exc)}", 502)

        if response.status_code == 401:
            raise GitHubClientError("Invalid or expired GitHub access token.", 401)
        elif response.status_code != 200:
            raise GitHubClientError(f"GitHub API error: HTTP {response.status_code}", response.status_code)

        return response.json()

    async def get_repository_details(
        self, access_token: str, owner: str, repo: str
    ) -> dict[str, Any]:
        """Fetch single repository details from GitHub API."""
        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Cryptanium-App",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/repos/{owner}/{repo}", headers=headers
                )
            except httpx.RequestError as exc:
                raise GitHubClientError(f"Network error connecting to GitHub API: {str(exc)}", 502)

        if response.status_code == 404:
            raise GitHubClientError(f"Repository '{owner}/{repo}' not found on GitHub.", 404)
        elif response.status_code != 200:
            raise GitHubClientError(f"GitHub API error: HTTP {response.status_code}", response.status_code)

        return response.json()
