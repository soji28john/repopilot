from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import ClassVar

from packages.retrieval.models import RepositoryFile


@dataclass(frozen=True)
class RepositoryChunk:
    """A searchable chunk extracted from a repository file."""

    path: str
    content: str
    language: str
    chunk_index: int
    start_line: int
    end_line: int


class RepositoryChunker:
    """Split repository files into searchable chunks."""

    DEFAULT_CHUNK_SIZE: ClassVar[int] = 80
    DEFAULT_OVERLAP: ClassVar[int] = 10

    LANGUAGE_MAP: ClassVar[dict[str, str]] = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".md": "markdown",
        ".txt": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".toml": "toml",
    }

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def detect_language(self, path: str) -> str:
        """Detect the language from the file extension."""

        suffix = PurePosixPath(path).suffix.lower()

        return self.LANGUAGE_MAP.get(suffix, "text")

    def chunk_file(
        self,
        path: str,
        content: str,
    ) -> list[RepositoryChunk]:
        """Split a repository file into overlapping line-based chunks."""

        if not content:
            return []

        lines = content.splitlines()
        chunks: list[RepositoryChunk] = []

        step = self.chunk_size - self.overlap
        chunk_index = 0
        start = 0

        while start < len(lines):
            end = min(
                start + self.chunk_size,
                len(lines),
            )

            chunk_content = "\n".join(lines[start:end])

            chunks.append(
                RepositoryChunk(
                    path=path,
                    content=chunk_content,
                    language=self.detect_language(path),
                    chunk_index=chunk_index,
                    start_line=start + 1,
                    end_line=end,
                )
            )

            if end == len(lines):
                break

            start += step
            chunk_index += 1

        return chunks

    def chunk_files(
        self,
        files: list[RepositoryFile],
    ) -> list[RepositoryChunk]:
        """Chunk multiple repository files."""

        chunks: list[RepositoryChunk] = []

        for repository_file in files:
            chunks.extend(
                self.chunk_file(
                    path=repository_file.path,
                    content=repository_file.content,
                )
            )

        return chunks
