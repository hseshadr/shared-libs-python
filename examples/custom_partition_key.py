"""Custom partition key demo: bucketed routing keyed by ``user_id``.

Same shape as ``basic_usage.py``, but the partition key is ``user_id`` (stored
in ``metadata`` instead of the legacy ``tenant_id`` field). The strategy hashes
``user_id`` into one of N buckets, isolating each user's vectors at search time.
"""

from __future__ import annotations

import asyncio

from shared_libs_python import BucketedPartitionStrategy, IndexManager
from shared_libs_python.vector_mgmt.core.types import VectorEmbedding
from shared_libs_python.vector_mgmt.testing import in_memory_factory


async def main() -> None:
    """Insert per-user embeddings and search a single user's slice."""
    strategy = BucketedPartitionStrategy(
        index_factory=in_memory_factory,
        num_buckets=16,
        partition_key_name="user_id",
    )
    manager = IndexManager(
        partition_strategy=strategy,
        partition_key_name="user_id",
    )

    embeddings = [
        VectorEmbedding(
            entity_id="doc_1",
            embedding=[0.1, 0.2, 0.3, 0.4],
            metadata={"user_id": "user_123", "category": "personal"},
        ),
        VectorEmbedding(
            entity_id="doc_2",
            embedding=[0.9, 0.8, 0.7, 0.6],
            metadata={"user_id": "user_456", "category": "work"},
        ),
    ]

    await manager.insert(embeddings)
    print(f"inserted {len(embeddings)} embeddings across user buckets")

    results = await manager.search(
        query_vector=[0.15, 0.25, 0.35, 0.45],
        k=10,
        partition_key="user_123",
    )
    print(f"top-{len(results)} matches for user_123:")
    for entity_id, distance in results:
        print(f"  {entity_id}  distance={distance:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
