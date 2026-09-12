import pytest

from packages.retrieval.chunking import RepositoryChunker
from packages.retrieval.models import RepositoryFile


def test_detect_python_language():
    chunker = RepositoryChunker()

    assert chunker.detect_language(
        "src/main.py"
    ) == "python"


def test_detect_typescript_language():
    chunker = RepositoryChunker()

    assert chunker.detect_language(
        "src/app.ts"
    ) == "typescript"


def test_detect_unknown_language_as_text():
    chunker = RepositoryChunker()

    assert chunker.detect_language(
        "Dockerfile"
    ) == "text"


def test_chunk_empty_file():
    chunker = RepositoryChunker()

    assert chunker.chunk_file(
        "empty.py",
        "",
    ) == []


def test_chunk_small_file():
    chunker = RepositoryChunker(
        chunk_size=3,
        overlap=1,
    )

    chunks = chunker.chunk_file(
        "main.py",
        "line 1\nline 2\nline 3",
    )

    assert len(chunks) == 1

    assert chunks[0].path == "main.py"
    assert chunks[0].language == "python"
    assert chunks[0].chunk_index == 0
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 3
    assert chunks[0].content == "line 1\nline 2\nline 3"


def test_chunk_large_file_with_overlap():
    chunker = RepositoryChunker(
        chunk_size=4,
        overlap=1,
    )

    content = "\n".join(
        f"line {number}"
        for number in range(1, 9)
    )

    chunks = chunker.chunk_file(
        "main.py",
        content,
    )

    assert len(chunks) == 3

    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 4

    assert chunks[1].start_line == 4
    assert chunks[1].end_line == 7

    assert chunks[2].start_line == 7
    assert chunks[2].end_line == 8


def test_chunk_files():
    chunker = RepositoryChunker(
        chunk_size=3,
        overlap=1,
    )

    files = [
        RepositoryFile(
            path="main.py",
            content="a\nb\nc",
            size=5,
        ),
        RepositoryFile(
            path="README.md",
            content="hello\nworld",
            size=11,
        ),
    ]

    chunks = chunker.chunk_files(files)

    assert len(chunks) == 2

    assert chunks[0].path == "main.py"
    assert chunks[0].language == "python"

    assert chunks[1].path == "README.md"
    assert chunks[1].language == "markdown"


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        RepositoryChunker(chunk_size=0)


def test_invalid_overlap():
    with pytest.raises(ValueError):
        RepositoryChunker(
            chunk_size=10,
            overlap=-1,
        )


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        RepositoryChunker(
            chunk_size=10,
            overlap=10,
        )
