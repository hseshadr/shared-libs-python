"""End-to-end demo: insert two embeddings, search, print real results.

Uses the bundled ``InMemoryVectorIndex`` reference factory so this script runs
cold against a fresh checkout. In production, swap ``in_memory_factory`` for a
factory that returns *your* ``VectorIndex`` implementation (FAISS, pgvector, …).
"""

from __future__ import annotations

import asyncio

from edgeproc_core import GlobalPartitionStrategy, IndexConfig, IndexManager
from edgeproc_core.vector_mgmt.core.types import VectorEmbedding
from edgeproc_core.vector_mgmt.testing import in_memory_factory


async def main() -> None:
    """Insert two tenant-tagged embeddings and run a tenant-scoped search."""
    config = IndexConfig(m=32, ef_construction=200, ef_search=100, dimension=4)
    strategy = GlobalPartitionStrategy(
        index_factory=in_memory_factory,
        index_name="global_index",
        config=config,
    )
    manager = IndexManager(partition_strategy=strategy)

    embeddings = [
        VectorEmbedding(
            entity_id="entity_1",
            embedding=[0.1, 0.2, 0.3, 0.4],
            tenant_id="tenant_1",
            metadata={"category": "documents"},
        ),
        VectorEmbedding(
            entity_id="entity_2",
            embedding=[0.2, 0.1, 0.4, 0.3],
            tenant_id="tenant_1",
            metadata={"category": "images"},
        ),
    ]

    await manager.insert(embeddings, partition_key="tenant_1")
    print(f"inserted {len(embeddings)} embeddings into tenant_1")

    results = await manager.search(
        query_vector=[0.15, 0.15, 0.35, 0.35],
        k=10,
        partition_key="tenant_1",
    )
    print(f"top-{len(results)} matches for tenant_1:")
    for entity_id, distance in results:
        print(f"  {entity_id}  distance={distance:.4f}")

    stats = await manager.get_stats(partition_key="tenant_1")
    print(f"stats: {stats[0].vector_count} vectors in {stats[0].index_name}")


if __name__ == "__main__":
    asyncio.run(main())
