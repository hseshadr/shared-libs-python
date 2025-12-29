"""Basic usage example with GlobalPartitionStrategy."""

import asyncio

from shared_libs_python import GlobalPartitionStrategy, IndexConfig, IndexManager
from shared_libs_python.vector_mgmt.core.types import VectorEmbedding


# Mock index factory for demonstration
async def create_mock_index(name: str, config: IndexConfig | None = None) -> None:
    """Mock index factory - replace with your actual VectorIndex implementation."""
    _ = config  # Unused in mock implementation
    print(f"Creating index: {name}")
    # In real usage, return your VectorIndex implementation
    # return YourVectorIndex(name, config)


async def main() -> None:
    """Basic usage example."""
    # Create index configuration
    config = IndexConfig(
        m=32,
        ef_construction=200,
        ef_search=100,
        dimension=1536,
    )

    # Setup partition strategy
    strategy = GlobalPartitionStrategy(
        index_factory=create_mock_index,
        index_name="global_index",
        config=config,
    )

    # Create manager
    manager = IndexManager(partition_strategy=strategy)

    # Create embeddings
    embeddings = [
        VectorEmbedding(
            entity_id="entity_1",
            embedding=[0.1] * 1536,  # Simplified for example
            tenant_id="tenant_1",
            metadata={"category": "documents"},
        ),
        VectorEmbedding(
            entity_id="entity_2",
            embedding=[0.2] * 1536,
            tenant_id="tenant_1",
            metadata={"category": "images"},
        ),
    ]

    # Insert embeddings
    await manager.insert(embeddings, partition_key="tenant_1")
    print("✓ Inserted embeddings")

    # Search
    query_vector = [0.15] * 1536
    results = await manager.search(
        query_vector=query_vector,
        k=10,
        partition_key="tenant_1",
    )
    print(f"✓ Found {len(results)} results")

    # Get statistics
    stats = await manager.get_stats(partition_key="tenant_1")
    print(f"✓ Index stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
