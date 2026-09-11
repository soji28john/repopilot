from typing import Any

import httpx

from packages.tools.github.auth import GitHubAppAuth


class GitHubClient:
    """Client for interacting with the GitHub API."""

    BASE_URL = "https://api.github.com"

    def __init__(self) -> None:
        self.auth = GitHubAppAuth()

    @staticmethod
    def _headers(token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_app_installations(self) -> list[dict[str, Any]]:
        """Return installations for the RepoPilot GitHub App."""

        jwt_token = self.auth.create_app_jwt()

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        ) as client:
            response = await client.get(
                "/app/installations",
                headers=self._headers(jwt_token),
            )

            response.raise_for_status()

            return response.json()

    async def create_installation_token(self) -> str:
        """Create a short-lived token for the GitHub App installation."""

        installation_id = self.auth.settings.github_installation_id
        jwt_token = self.auth.create_app_jwt()

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        ) as client:
            response = await client.post(
                f"/app/installations/{installation_id}/access_tokens",
                headers=self._headers(jwt_token),
            )

            response.raise_for_status()

            data = response.json()

            return data["token"]

    async def get_repository(
        self,
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """Get repository metadata using the installation token."""

        token = await self.create_installation_token()

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        ) as client:
            response = await client.get(
                f"/repos/{owner}/{repo}",
                headers=self._headers(token),
            )

            response.raise_for_status()
    
            return response.json()
    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[dict[str, Any]]:
        """Return the repository file tree."""

        token = await self.create_installation_token()

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        ) as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/git/trees/{branch}",
                headers=self._headers(token),
                params={"recursive": "1"},
            )

            response.raise_for_status()

            data = response.json()

            return data["tree"]

    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str,
    ) -> str:
        """Return decoded text content for a repository file."""

        import base64

        token = await self.create_installation_token()

        async with httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0,
        ) as client:
            response = await client.get(
                f"/repos/{owner}/{repo}/contents/{path}",
                headers=self._headers(token),
                params={"ref": ref},
            )

            response.raise_for_status()

            data = response.json()
            content = data["content"]

            decoded = base64.b64decode(content)

            return decoded.decode("utf-8")
