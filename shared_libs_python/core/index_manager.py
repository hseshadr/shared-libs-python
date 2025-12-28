"""Index manager for coordinating vector indices."""

from typing import Any

from shared_libs_python.core.types import IndexConfig, IndexStats, VectorEmbedding
from shared_libs_python.partitioning.strategies import PartitionStrategy


class IndexManager:
    """Manages vector indices with partitioning strategy."""

    def __init__(
        self,
        partition_strategy: PartitionStrategy,
        default_config: IndexConfig | None = None,
        partition_key_name: str = "tenant_id",
    ) -> None:
        """
        Initialize index manager.
        
        Args:
            partition_strategy: Strategy for partitioning indices
            default_config: Default index configuration
            partition_key_name: Name of the partition key used for filtering (e.g., 'tenant_id', 'user_id')
        """
        self.partition_strategy = partition_strategy
        self.default_config = default_config or IndexConfig()
        self.partition_key_name = partition_key_name

    async def insert(
        self,
        embeddings: list[VectorEmbedding],
        partition_key: str | None = None,
    ) -> None:
        """
        Insert embeddings using partition strategy.
        
        Args:
            embeddings: List of embeddings to insert
            partition_key: Optional partition key value (used as fallback if not in embedding metadata)
        """
        partitions = self.partition_strategy.get_partitions(embeddings, partition_key)
        for partition_name, partition_embeddings in partitions.items():
            index = await self.partition_strategy.get_index(partition_name)
            await index.insert(partition_embeddings)

    async def search(
        self,
        query_vector: list[float],
        k: int,
        partition_key: str | None = None,
        filters: dict[str, Any] | None = None,
        ef_search: int | None = None,
    ) -> list[tuple[str, float]]:
        """
        Search across partitions using partition strategy.
        
        Args:
            query_vector: Query vector for similarity search
            k: Number of results to return
            partition_key: Partition key value to filter by
            filters: Additional filters to apply
            ef_search: HNSW ef_search parameter override
            
        Returns:
            List of (entity_id, distance) tuples
        """
        search_filters = filters or {}
        if partition_key:
            search_filters[self.partition_key_name] = partition_key

        partitions = self.partition_strategy.get_search_partitions(partition_key)
        results: list[tuple[str, float]] = []

        for partition_name in partitions:
            index = await self.partition_strategy.get_index(partition_name)
            partition_results = await index.search(
                query_vector, k=k, filters=search_filters, ef_search=ef_search
            )
            results.extend(partition_results)

        # Merge and deduplicate by entity_id, keeping best score
        seen: dict[str, float] = {}
        for entity_id, distance in results:
            if entity_id not in seen or distance < seen[entity_id]:
                seen[entity_id] = distance

        # Sort by distance and return top K
        sorted_results = sorted(seen.items(), key=lambda x: x[1])
        return sorted_results[:k]

    async def delete(
        self,
        entity_ids: list[str],
        partition_key: str | None = None,
    ) -> None:
        """
        Delete embeddings across partitions.
        
        Args:
            entity_ids: List of entity IDs to delete
            partition_key: Partition key value to scope deletion
        """
        partitions = self.partition_strategy.get_search_partitions(partition_key)
        for partition_name in partitions:
            index = await self.partition_strategy.get_index(partition_name)
            await index.delete(entity_ids)

    async def get_stats(self, partition_key: str | None = None) -> list[IndexStats]:
        """
        Get statistics for relevant partitions.
        
        Args:
            partition_key: Partition key value to scope statistics
            
        Returns:
            List of index statistics
        """
        partitions = self.partition_strategy.get_search_partitions(partition_key)
        stats: list[IndexStats] = []

        for partition_name in partitions:
            index = await self.partition_strategy.get_index(partition_name)
            stat = await index.get_stats()
            stats.append(stat)

        return stats

    async def rebuild_if_needed(
        self,
        partition_key: str | None = None,
        force: bool = False,
    ) -> bool:
        """
        Check if rebuild is needed and trigger if so.
        
        Args:
            partition_key: Partition key value to scope rebuild check
            force: Force rebuild regardless of conditions
            
        Returns:
            True if rebuild was triggered, False otherwise
        """
        stats_list = await self.get_stats(partition_key)
        for stats in stats_list:
            needs_rebuild = (
                force
                or stats.tombstone_percentage > 10.0
                or stats.index_size_mb > 1000.0  # Example threshold
            )

            if needs_rebuild:
                partition_name = stats.index_name
                index = await self.partition_strategy.get_index(partition_name)
                await index.rebuild()
                return True

        return False

