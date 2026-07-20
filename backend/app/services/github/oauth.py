from typing import Any
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.database.schemas import GitHubUserData


class GitHubOAuthError(Exception):
    """Custom exception raised when GitHub OAuth interaction fails."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GitHubOAuthService:
    """Service handling GitHub OAuth authentication and user info retrieval using httpx."""

    GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_URL = "https://api.github.com/user"
    GITHUB_EMAILS_URL = "https://api.github.com/user/emails"

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        self.client_id = client_id or settings.GITHUB_CLIENT_ID
        self.client_secret = client_secret or settings.GITHUB_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.GITHUB_REDIRECT_URI

    def get_authorization_url(self, state: str | None = None) -> str:
        """Construct the GitHub OAuth authorization URL."""
        if not self.client_id:
            raise GitHubOAuthError(
                "GITHUB_CLIENT_ID is not configured in environment.", 500
            )

        params: dict[str, str] = {
            "client_id": self.client_id,
            "scope": "read:user user:email",
        }
        if self.redirect_uri:
            params["redirect_uri"] = self.redirect_uri
        if state:
            params["state"] = state

        return f"{self.GITHUB_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> str:
        """Exchange authorization code for a GitHub access token using httpx."""
        if not self.client_id or not self.client_secret:
            raise GitHubOAuthError(
                "GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be configured.",
                500,
            )

        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        if self.redirect_uri:
            payload["redirect_uri"] = self.redirect_uri

        headers = {
            "Accept": "application/json",
            "User-Agent": "Cryptanium-OAuth",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    self.GITHUB_TOKEN_URL, data=payload, headers=headers
                )
            except httpx.RequestError as exc:
                raise GitHubOAuthError(
                    f"Failed to contact GitHub OAuth server: {str(exc)}", 502
                )

        if response.status_code != 200:
            raise GitHubOAuthError(
                f"GitHub token endpoint returned status code {response.status_code}",
                400,
            )

        data = response.json()
        if "error" in data:
            error_desc = data.get("error_description", data["error"])
            raise GitHubOAuthError(
                f"GitHub OAuth error: {error_desc}", 400
            )

        access_token = data.get("access_token")
        if not access_token:
            raise GitHubOAuthError("No access_token returned by GitHub.", 400)

        return access_token

    async def fetch_user_profile(self, access_token: str) -> GitHubUserData:
        """Fetch authenticated user information from GitHub API using httpx."""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "User-Agent": "Cryptanium-OAuth",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(self.GITHUB_USER_URL, headers=headers)
            except httpx.RequestError as exc:
                raise GitHubOAuthError(
                    f"Failed to fetch GitHub user profile: {str(exc)}", 502
                )

            if response.status_code != 200:
                detail = self._response_detail(response)
                raise GitHubOAuthError(
                    f"Failed to fetch GitHub user profile: HTTP {response.status_code} - {detail}",
                    400,
                )

            try:
                user_data = response.json()
            except ValueError as exc:
                raise GitHubOAuthError(
                    f"GitHub returned invalid profile data: {exc}", 502
                ) from exc
            if not user_data.get("id") or not user_data.get("login"):
                raise GitHubOAuthError("GitHub profile is missing id or login.", 502)
            email = user_data.get("email")

            # Fallback to /user/emails if email is private/null
            if not email:
                email = await self._fetch_primary_email(client, headers)

            return GitHubUserData(
                id=str(user_data["id"]),
                username=user_data.get("login", ""),
                email=email,
                avatar_url=user_data.get("avatar_url"),
            )

    async def _fetch_primary_email(
        self, client: httpx.AsyncClient, headers: dict[str, str]
    ) -> str | None:
        """Fallback method to retrieve primary email from GitHub user/emails endpoint."""
        try:
            res = await client.get(self.GITHUB_EMAILS_URL, headers=headers)
            if res.status_code == 200:
                emails: list[dict[str, Any]] = res.json()
                for item in emails:
                    if item.get("primary") and item.get("verified"):
                        return item.get("email")
                if emails:
                    return emails[0].get("email")
        except httpx.RequestError:
            pass
        return None

    @staticmethod
    def _response_detail(response: httpx.Response) -> str:
        """Return a safe, useful upstream error without exposing credentials."""
        try:
            payload = response.json()
            return str(payload.get("message") or payload.get("error") or "unknown error")
        except ValueError:
            return response.text[:200] or "empty response"
