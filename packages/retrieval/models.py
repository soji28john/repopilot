from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryFile:
    """A source file retrieved from a GitHub repository."""

    path: str
    content: str
    size: int
