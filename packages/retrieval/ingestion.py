from typing import ClassVar

from packages.retrieval.models import RepositoryFile
from packages.tools.github.client import GitHubClient


class RepositoryIngestor:
    """Discover and retrieve relevant files from a GitHub repository."""

    IGNORED_DIRECTORIES: ClassVar[set[str]] = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }

    SUPPORTED_EXTENSIONS: ClassVar[set[str]] = {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
    }

    def __init__(
        self,
        github_client: GitHubClient | None = None,
    ) -> None:
        self.github_client = github_client or GitHubClient()

    def should_include(self, path: str) -> bool:
        """Determine whether a repository path should be ingested."""

        parts = path.split("/")

        if any(
            part in self.IGNORED_DIRECTORIES
            for part in parts
        ):
            return False

        filename = parts[-1]

        if "." not in filename:
            return False

        extension = "." + filename.rsplit(".", 1)[-1].lower()

        return extension in self.SUPPORTED_EXTENSIONS

    async def ingest(
        self,
        owner: str,
        repo: str,
        branch: str,
    ) -> list[RepositoryFile]:
        """Retrieve supported source files from a repository."""

        tree = await self.github_client.get_repository_tree(
            owner=owner,
            repo=repo,
            branch=branch,
        )

        files: list[RepositoryFile] = []

        for entry in tree:
            if entry.get("type") != "blob":
                continue

            path = entry["path"]

            if not self.should_include(path):
                continue

            content = await self.github_client.get_file_content(
                owner=owner,
                repo=repo,
                path=path,
                ref=branch,
            )

            files.append(
                RepositoryFile(
                    path=path,
                    content=content,
                    size=len(content.encode("utf-8")),
                )
            )

        return files
