from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from packages.tools.github.client import GitHubClient


@pytest.mark.asyncio
async def test_get_app_installations():
    client = GitHubClient()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [
        {
            "id": 123,
            "account": {
                "login": "test-user",
            },
        }
    ]

    with patch(
        "packages.tools.github.client.httpx.AsyncClient"
    ) as mock_client:
        mock_context = AsyncMock()
        mock_context.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_context

        with patch.object(
            client.auth,
            "create_app_jwt",
            return_value="test-jwt",
        ):
            result = await client.get_app_installations()

    assert len(result) == 1
    assert result[0]["id"] == 123

    mock_context.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_installation_token():
    client = GitHubClient()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "token": "test-installation-token",
    }

    with patch(
        "packages.tools.github.client.httpx.AsyncClient"
    ) as mock_client:
        mock_context = AsyncMock()
        mock_context.post.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_context

        with patch.object(
            client.auth,
            "create_app_jwt",
            return_value="test-jwt",
        ):
            token = await client.create_installation_token()

    assert token == "test-installation-token"

    mock_context.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_repository():
    client = GitHubClient()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "full_name": "test-user/test-repo",
        "private": False,
        "default_branch": "main",
    }

    with patch(
        "packages.tools.github.client.httpx.AsyncClient"
    ) as mock_client:
        mock_context = AsyncMock()
        mock_context.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_context

        with patch.object(
            client,
            "create_installation_token",
            new=AsyncMock(return_value="test-token"),
        ):
            result = await client.get_repository(
                owner="test-user",
                repo="test-repo",
            )

    assert result["full_name"] == "test-user/test-repo"
    assert result["default_branch"] == "main"

    mock_context.get.assert_awaited_once()
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

@pytest.mark.asyncio
async def test_get_repository_tree():
    client = GitHubClient()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "packages/example.py", "type": "blob"},
        ]
    }

    with patch(
        "packages.tools.github.client.httpx.AsyncClient"
    ) as mock_client:
        mock_context = AsyncMock()
        mock_context.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_context

        with patch.object(
            client,
            "create_installation_token",
            new=AsyncMock(return_value="test-token"),
        ):
            result = await client.get_repository_tree(
                owner="soji28john",
                repo="repopilot",
                branch="main",
            )

    assert len(result) == 2
    assert result[0]["path"] == "README.md"

    mock_context.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_file_content():
    client = GitHubClient()

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None

    import base64

    encoded = base64.b64encode(b"print('hello')").decode()

    mock_response.json.return_value = {
        "content": encoded,
    }

    with patch(
        "packages.tools.github.client.httpx.AsyncClient"
    ) as mock_client:
        mock_context = AsyncMock()
        mock_context.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_context

        with patch.object(
            client,
            "create_installation_token",
            new=AsyncMock(return_value="test-token"),
        ):
            result = await client.get_file_content(
                owner="soji28john",
                repo="repopilot",
                path="main.py",
                ref="main",
            )

    assert result == "print('hello')"

    mock_context.get.assert_awaited_once()            


            
