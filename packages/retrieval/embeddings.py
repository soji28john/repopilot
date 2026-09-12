from dataclasses import dataclass
from typing import Protocol

from packages.retrieval.chunking import RepositoryChunk


@dataclass(frozen=True)
class EmbeddedChunk:
    """A repository chunk together with its embedding vector."""

    chunk: RepositoryChunk
    vector: list[float]
    model: str
    dimensions: int


class EmbeddingProvider(Protocol):
    """Interface implemented by embedding providers."""

    @property
    def model(self) -> str:
        """Return the embedding model name."""

    @property
    def dimensions(self) -> int:
        """Return the embedding vector dimensions."""

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""


class DeterministicEmbeddingProvider:
    """Deterministic embedding provider for local development and tests."""

    def __init__(
        self,
        dimensions: int = 8,
    ) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")

        self._dimensions = dimensions

    @property
    def model(self) -> str:
        """Return the local embedding model name."""

        return "deterministic-test"

    @property
    def dimensions(self) -> int:
        """Return the configured embedding dimensions."""

        return self._dimensions

    async def embed(self, text: str) -> list[float]:
        """Generate a deterministic vector from text."""

        vector = [0.0] * self._dimensions

        if not text:
            return vector

        for index, character in enumerate(text):
            vector[index % self._dimensions] += (
                ord(character) / 1000.0
            )

        magnitude = sum(value * value for value in vector) ** 0.5

        if magnitude == 0:
            return vector

        return [
            value / magnitude
            for value in vector
        ]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate deterministic embeddings for multiple texts."""

        return [
            await self.embed(text)
            for text in texts
        ]


class ChunkEmbedder:
    """Generate embeddings for repository chunks."""

    def __init__(
        self,
        provider: EmbeddingProvider,
    ) -> None:
        self.provider = provider

    async def embed_chunks(
        self,
        chunks: list[RepositoryChunk],
    ) -> list[EmbeddedChunk]:
        """Embed repository chunks while preserving their metadata."""

        if not chunks:
            return []

        vectors = await self.provider.embed_batch(
            [chunk.content for chunk in chunks]
        )

        if len(vectors) != len(chunks):
            raise ValueError(
                "Embedding provider returned an unexpected number "
                "of vectors"
            )

        return [
            EmbeddedChunk(
                chunk=chunk,
                vector=vector,
                model=self.provider.model,
                dimensions=self.provider.dimensions,
            )
            for chunk, vector in zip(
                chunks,
                vectors,
                strict=True,
            )
        ]
