"""Partitioning strategy implementations."""

from __future__ import annotations

import asyncio
import hashlib
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Final

from shared_libs_python.vector_mgmt.core.types import (
    IndexConfig,
    IndexFactory,
    VectorEmbedding,
    VectorIndex,
)

PartitionKeyExtractor = Callable[[VectorEmbedding], str | None]


class PartitionStrategy(ABC):
    """Abstract base class for partitioning strategies."""

    def __init__(
        self,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: PartitionKeyExtractor | None = None,
    ) -> None:
        """Configure the partition key name and (optional) custom extractor."""
        self.partition_key_name = partition_key_name
        self._extract_key: PartitionKeyExtractor = (
            partition_key_extractor
            if partition_key_extractor is not None
            else (lambda emb: emb.get_partition_key(partition_key_name))
        )

    @abstractmethod
    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """Partition ``embeddings`` into ``{partition_name: [embedding, ...]}`` groups."""
        ...

    @abstractmethod
    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Return the partition names to search for ``partition_key``."""
        ...

    @abstractmethod
    async def get_index(self, partition_name: str) -> VectorIndex:
        """Return the index instance for ``partition_name``."""
        ...


class GlobalPartitionStrategy(PartitionStrategy):
    """Single global index with metadata filtering."""

    def __init__(
        self,
        index_factory: IndexFactory,
        index_name: str = "global_index",
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: PartitionKeyExtractor | None = None,
    ) -> None:
        """Initialize the global partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.index_name = index_name
        self.config = config
        self._index: VectorIndex | None = None
        self._creation_lock = asyncio.Lock()

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """All embeddings go to a single global partition."""
        return {self.index_name: embeddings}

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Always search the single global partition."""
        return [self.index_name]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Lazily create and cache the global index (safe under concurrent calls)."""
        if self._index is None:
            async with self._creation_lock:
                if self._index is None:
                    self._index = await self.index_factory(self.index_name, config=self.config)
        return self._index


class BucketedPartitionStrategy(PartitionStrategy):
    """Hash-based bucketing strategy."""

    def __init__(
        self,
        index_factory: IndexFactory,
        num_buckets: int = 256,
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: PartitionKeyExtractor | None = None,
    ) -> None:
        """Initialize the bucketed partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.num_buckets = num_buckets
        self.config = config
        self._indices: dict[str, VectorIndex] = {}
        self._creation_lock = asyncio.Lock()

    def _get_bucket_id(self, partition_key: str | None) -> int:
        """Compute the bucket id for a partition key (``None`` → bucket 0).

        Uses a SHA-256 digest of the UTF-8 encoded key — NOT the builtin
        ``hash()``, which is randomized per process (PYTHONHASHSEED) and would
        make persisted bucket assignments unstable across runs.
        """
        if partition_key is None:
            return 0
        digest = hashlib.sha256(partition_key.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big") % self.num_buckets

    def _get_partition_name(self, bucket_id: int) -> str:
        """Return the partition name corresponding to ``bucket_id``."""
        return f"bucket_{bucket_id}"

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """Bucket embeddings by partition key, falling back to ``partition_key``."""
        buckets: dict[str, list[VectorEmbedding]] = {}
        for emb in embeddings:
            emb_partition_key = self._extract_key(emb) or partition_key
            partition_name = self._get_partition_name(self._get_bucket_id(emb_partition_key))
            buckets.setdefault(partition_name, []).append(emb)
        return buckets

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Return the single bucket ``partition_key`` hashes into."""
        return [self._get_partition_name(self._get_bucket_id(partition_key))]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Lazily create and cache the index for ``partition_name`` (concurrency-safe)."""
        if partition_name not in self._indices:
            async with self._creation_lock:
                if partition_name not in self._indices:
                    self._indices[partition_name] = await self.index_factory(
                        partition_name, config=self.config
                    )
        return self._indices[partition_name]


_TIER_FACTORY_NAMES: Final[dict[str, str]] = {"hot": "hot_index", "cold": "cold_index"}
"""Maps two-tier partition names to the index names handed to the factory."""


class TwoTierPartitionStrategy(PartitionStrategy):
    """Hot/cold two-tier strategy keyed on a ``created_at`` metadata field."""

    def __init__(
        self,
        index_factory: IndexFactory,
        hot_retention_days: int = 30,
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: PartitionKeyExtractor | None = None,
    ) -> None:
        """Initialize the two-tier partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.hot_retention_days = hot_retention_days
        self.config = config
        self._indices: dict[str, VectorIndex] = {}
        self._creation_lock = asyncio.Lock()

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """Classify each embedding as hot or cold based on its ``created_at``."""
        cutoff_date = datetime.now() - timedelta(days=self.hot_retention_days)
        tiered: dict[str, list[VectorEmbedding]] = {}
        for emb in embeddings:
            tiered.setdefault(_classify_embedding(emb, cutoff_date), []).append(emb)
        return tiered

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Search both hot and cold partitions."""
        return ["hot", "cold"]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Lazily create and cache the hot or cold index (concurrency-safe)."""
        factory_name = _TIER_FACTORY_NAMES.get(partition_name)
        if factory_name is None:
            raise ValueError(f"Unknown partition: {partition_name}")
        if partition_name not in self._indices:
            async with self._creation_lock:
                if partition_name not in self._indices:
                    self._indices[partition_name] = await self.index_factory(
                        factory_name, config=self.config
                    )
        return self._indices[partition_name]


def _classify_embedding(emb: VectorEmbedding, cutoff_date: datetime) -> str:
    """Return ``"hot"`` or ``"cold"`` for ``emb`` based on ``metadata['created_at']``."""
    created_at = emb.metadata.get("created_at")
    if not isinstance(created_at, str) or not created_at:
        return "hot"
    try:
        emb_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        return "hot" if emb_date > cutoff_date else "cold"
    except (ValueError, AttributeError):
        return "cold"
