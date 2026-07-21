from typing import Any

import httpx

from app.database.schemas import RepositoryResponse


class GitHubRepositoryError(Exception):
    """Custom exception raised when GitHub Repository API calls fail."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GitHubRepositoryService:
    """Service for fetching user repositories from GitHub REST API using httpx."""

    GITHUB_REPOS_URL = "https://api.github.com/user/repos"

    async def fetch_user_repositories(
        self, access_token: str, visibility: str = "all", sort: str = "updated", per_page: int = 100
    ) -> list[RepositoryResponse]:
        """Fetch repositories for the authenticated GitHub user using an access token."""
        if not access_token or not access_token.strip():
            raise GitHubRepositoryError("GitHub access token is required.", 401)

        headers = {
            "Authorization": f"Bearer {access_token.strip()}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Cryptanium-App",
        }
        params = {
            "visibility": visibility,
            "sort": sort,
            "per_page": per_page,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(
                    self.GITHUB_REPOS_URL, headers=headers, params=params
                )
            except httpx.RequestError as exc:
                raise GitHubRepositoryError(
                    f"Failed to connect to GitHub API: {str(exc)}", 502
                )

        if response.status_code == 401:
            raise GitHubRepositoryError("Invalid or expired GitHub access token.", 401)
        elif response.status_code == 403:
            raise GitHubRepositoryError(
                "GitHub API rate limit exceeded or access forbidden.", 403
            )
        elif response.status_code != 200:
            raise GitHubRepositoryError(
                f"GitHub API returned error: HTTP {response.status_code}",
                response.status_code if 400 <= response.status_code < 600 else 500,
            )

        repos_data: list[dict[str, Any]] = response.json()
        repositories: list[RepositoryResponse] = []

        for repo in repos_data:
            owner_login = ""
            if isinstance(repo.get("owner"), dict):
                owner_login = repo["owner"].get("login", "")

            repositories.append(
                RepositoryResponse(
                    id=int(repo["id"]) if repo.get("id") is not None else None,
                    github_repo_id=str(repo.get("id", "")) or None,
                    name=repo.get("name", ""),
                    owner=owner_login,
                    full_name=repo.get("full_name") or (f"{owner_login}/{repo.get('name', '')}" if owner_login else repo.get("name", "")),
                    private=bool(repo.get("private", False)),
                    language=repo.get("language"),
                    default_branch=repo.get("default_branch", "main"),
                    visibility="private" if repo.get("private") else "public",
                    clone_url=repo.get("clone_url"),
                    updated_at=repo.get("updated_at"),
                )
            )

        return repositories
