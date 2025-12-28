"""Partitioning strategy implementations."""

from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any, Callable

from shared_libs_python.core.types import IndexConfig, VectorEmbedding, VectorIndex


class PartitionStrategy(ABC):
    """Abstract base class for partitioning strategies."""

    def __init__(
        self,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: Callable[[VectorEmbedding], str | None] | None = None,
    ) -> None:
        """
        Initialize partition strategy.
        
        Args:
            partition_key_name: Name of the partition key (e.g., 'tenant_id', 'user_id', 'org_id')
            partition_key_extractor: Optional custom function to extract partition key from embedding.
                                    If None, uses embedding.get_partition_key(partition_key_name)
        """
        self.partition_key_name = partition_key_name
        if partition_key_extractor is None:
            self._extract_key: Callable[[VectorEmbedding], str | None] = (
                lambda emb: emb.get_partition_key(partition_key_name)
            )
        else:
            self._extract_key = partition_key_extractor

    @abstractmethod
    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """
        Partition embeddings into index groups.
        
        Args:
            embeddings: List of embeddings to partition
            partition_key: Optional partition key value. If provided, used as fallback
                          when embeddings don't have the key in metadata.
        
        Returns: Dict mapping partition_name -> list of embeddings
        """
        ...

    @abstractmethod
    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """
        Get partition names to search for a given partition key.
        
        Args:
            partition_key: Partition key value to search for
        
        Returns: List of partition names
        """
        ...

    @abstractmethod
    async def get_index(self, partition_name: str) -> VectorIndex:
        """Get index instance for partition."""
        ...


class GlobalPartitionStrategy(PartitionStrategy):
    """Single global index with metadata filtering."""

    def __init__(
        self,
        index_factory: Callable[..., Awaitable[VectorIndex]],
        index_name: str = "global_index",
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: Callable[[VectorEmbedding], str | None] | None = None,
    ) -> None:
        """Initialize global partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.index_name = index_name
        self.config = config
        self._index: VectorIndex | None = None

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """All embeddings go to single global partition."""
        return {self.index_name: embeddings}

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Search single global partition."""
        return [self.index_name]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Get or create global index."""
        if self._index is None:
            self._index = await self.index_factory(
                self.index_name, config=self.config
            )
        return self._index


class BucketedPartitionStrategy(PartitionStrategy):
    """Hash-based bucketing strategy."""

    def __init__(
        self,
        index_factory: Callable[..., Awaitable[VectorIndex]],
        num_buckets: int = 256,
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: Callable[[VectorEmbedding], str | None] | None = None,
    ) -> None:
        """Initialize bucketed partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.num_buckets = num_buckets
        self.config = config
        self._indices: dict[str, VectorIndex] = {}

    def _get_bucket_id(self, partition_key: str | None) -> int:
        """Compute bucket ID from partition key hash."""
        if partition_key is None:
            return 0  # Global entities in bucket 0
        return hash(partition_key) % self.num_buckets

    def _get_partition_name(self, bucket_id: int) -> str:
        """Get partition name for bucket."""
        return f"bucket_{bucket_id}"

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """Partition embeddings by bucket."""
        buckets: dict[str, list[VectorEmbedding]] = {}

        for emb in embeddings:
            # Extract partition key from embedding, fallback to parameter
            emb_partition_key: str | None = self._extract_key(emb) or partition_key
            bucket_id = self._get_bucket_id(emb_partition_key)
            partition_name = self._get_partition_name(bucket_id)

            if partition_name not in buckets:
                buckets[partition_name] = []
            buckets[partition_name].append(emb)

        return buckets

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Get partition to search for partition key."""
        bucket_id = self._get_bucket_id(partition_key)
        return [self._get_partition_name(bucket_id)]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Get or create index for partition."""
        if partition_name not in self._indices:
            self._indices[partition_name] = await self.index_factory(
                partition_name, config=self.config
            )
        return self._indices[partition_name]


class TwoTierPartitionStrategy(PartitionStrategy):
    """Hot/cold two-tier strategy."""

    def __init__(
        self,
        index_factory: Callable[..., Awaitable[VectorIndex]],
        hot_retention_days: int = 30,
        config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
        partition_key_extractor: Callable[[VectorEmbedding], str | None] | None = None,
    ) -> None:
        """Initialize two-tier partition strategy."""
        super().__init__(partition_key_name, partition_key_extractor)
        self.index_factory = index_factory
        self.hot_retention_days = hot_retention_days
        self.config = config
        self._hot_index: VectorIndex | None = None
        self._cold_index: VectorIndex | None = None

    def get_partitions(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> dict[str, list[VectorEmbedding]]:
        """Partition embeddings into hot/cold based on metadata."""
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=self.hot_retention_days)
        hot: list[VectorEmbedding] = []
        cold: list[VectorEmbedding] = []

        for emb in embeddings:
            created_at = emb.metadata.get("created_at")
            if created_at and isinstance(created_at, str):
                try:
                    emb_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if emb_date > cutoff_date:
                        hot.append(emb)
                    else:
                        cold.append(emb)
                except (ValueError, AttributeError):
                    # If date parsing fails, default to cold
                    cold.append(emb)
            else:
                # No date, default to hot (newer data)
                hot.append(emb)

        partitions: dict[str, list[VectorEmbedding]] = {}
        if hot:
            partitions["hot"] = hot
        if cold:
            partitions["cold"] = cold

        return partitions

    def get_search_partitions(self, partition_key: str | None = None) -> list[str]:
        """Search both hot and cold partitions."""
        return ["hot", "cold"]

    async def get_index(self, partition_name: str) -> VectorIndex:
        """Get or create index for partition."""
        if partition_name == "hot":
            if self._hot_index is None:
                self._hot_index = await self.index_factory(
                    "hot_index", config=self.config
                )
            return self._hot_index
        elif partition_name == "cold":
            if self._cold_index is None:
                self._cold_index = await self.index_factory(
                    "cold_index", config=self.config
                )
            return self._cold_index
        else:
            raise ValueError(f"Unknown partition: {partition_name}")

