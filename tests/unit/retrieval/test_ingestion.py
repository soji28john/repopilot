from unittest.mock import AsyncMock

import pytest

from packages.retrieval.ingestion import RepositoryIngestor


def test_should_include_supported_python_file():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include("apps/api/main.py") is True


def test_should_include_supported_markdown_file():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include("README.md") is True


def test_should_ignore_virtual_environment():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include(".venv/lib/example.py") is False


def test_should_ignore_node_modules():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include("node_modules/package/index.js") is False


def test_should_ignore_unsupported_file():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include("image.png") is False


def test_should_ignore_file_without_extension():
    ingestor = RepositoryIngestor()

    assert ingestor.should_include("Dockerfile") is False


@pytest.mark.asyncio
async def test_ingest_repository_files():
    github_client = AsyncMock()

    github_client.get_repository_tree.return_value = [
        {"path": "README.md", "type": "blob"},
        {"path": "main.py", "type": "blob"},
        {"path": "image.png", "type": "blob"},
        {"path": "src/__pycache__/cached.py", "type": "blob"},
        {"path": "src", "type": "tree"},
    ]

    github_client.get_file_content.side_effect = [
        "# RepoPilot",
        "print('hello')",
    ]

    ingestor = RepositoryIngestor(github_client)

    files = await ingestor.ingest(
        owner="soji28john",
        repo="repopilot",
        branch="main",
    )

    assert len(files) == 2

    assert files[0].path == "README.md"
    assert files[0].content == "# RepoPilot"

    assert files[1].path == "main.py"
    assert files[1].content == "print('hello')"

    assert files[0].size == len(b"# RepoPilot")
    assert files[1].size == len(b"print('hello')")

    github_client.get_repository_tree.assert_awaited_once_with(
        owner="soji28john",
        repo="repopilot",
        branch="main",
    )

    assert github_client.get_file_content.await_count == 2
