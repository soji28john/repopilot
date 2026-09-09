from unittest.mock import AsyncMock, MagicMock, patch

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
