import pytest

from packages.tools.github.client import GitHubClient


@pytest.mark.asyncio
async def test_get_repository():
    client = GitHubClient()

    repository = await client.get_repository(
        owner="soji28john",
        repo="repopilot",
    )

    assert repository["full_name"] == "soji28john/repopilot"
    assert repository["default_branch"] == "main"
