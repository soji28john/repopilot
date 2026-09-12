import pytest

from packages.retrieval.chunking import RepositoryChunk
from packages.retrieval.embeddings import (
    ChunkEmbedder,
    DeterministicEmbeddingProvider,
)


def make_chunk(
    content: str,
    index: int = 0,
) -> RepositoryChunk:
    return RepositoryChunk(
        path="src/main.py",
        content=content,
        language="python",
        chunk_index=index,
        start_line=1,
        end_line=1,
    )


@pytest.mark.asyncio
async def test_embed_returns_expected_dimensions():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vector = await provider.embed("hello")

    assert len(vector) == 8


@pytest.mark.asyncio
async def test_embed_is_deterministic():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    first = await provider.embed("hello")
    second = await provider.embed("hello")

    assert first == second


@pytest.mark.asyncio
async def test_different_text_produces_different_embedding():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    first = await provider.embed("hello")
    second = await provider.embed("different")

    assert first != second


@pytest.mark.asyncio
async def test_empty_text_returns_zero_vector():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vector = await provider.embed("")

    assert vector == [0.0] * 8


@pytest.mark.asyncio
async def test_embedding_is_normalized():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vector = await provider.embed("hello")

    magnitude = sum(
        value * value
        for value in vector
    ) ** 0.5

    assert magnitude == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_embed_batch():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vectors = await provider.embed_batch(
        ["one", "two", "three"]
    )

    assert len(vectors) == 3
    assert all(len(vector) == 8 for vector in vectors)


@pytest.mark.asyncio
async def test_embed_chunks_preserves_metadata():
    provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    embedder = ChunkEmbedder(provider)

    chunks = [
        make_chunk("def hello():", index=0),
        make_chunk("    return 'hello'", index=1),
    ]

    embedded = await embedder.embed_chunks(chunks)

    assert len(embedded) == 2

    assert embedded[0].chunk.path == "src/main.py"
    assert embedded[0].chunk.chunk_index == 0
    assert embedded[0].chunk.language == "python"

    assert embedded[0].model == "deterministic-test"
    assert embedded[0].dimensions == 8
    assert len(embedded[0].vector) == 8


@pytest.mark.asyncio
async def test_embed_empty_chunks():
    provider = DeterministicEmbeddingProvider()

    embedder = ChunkEmbedder(provider)

    result = await embedder.embed_chunks([])

    assert result == []


def test_invalid_embedding_dimensions():
    with pytest.raises(ValueError):
        DeterministicEmbeddingProvider(
            dimensions=0,
        )
