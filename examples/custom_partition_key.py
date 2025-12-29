"""Example using custom partition keys (user_id instead of tenant_id)."""

import asyncio

from shared_libs_python import BucketedPartitionStrategy, IndexConfig, IndexManager
from shared_libs_python.vector_mgmt.core.types import VectorEmbedding


async def create_mock_index(name: str, config: IndexConfig | None = None) -> None:
    """Mock index factory."""
    _ = config  # Unused in mock implementation
    print(f"Creating index: {name}")


async def main() -> None:
    """Example with user_id as partition key."""
    # Setup strategy with user_id as partition key
    strategy = BucketedPartitionStrategy(
        index_factory=create_mock_index,
        num_buckets=256,
        partition_key_name="user_id",  # Use user_id instead of tenant_id
    )

    # Create manager with matching partition key name
    manager = IndexManager(
        partition_strategy=strategy,
        partition_key_name="user_id",
    )

    # Embeddings with user_id in metadata
    embeddings = [
        VectorEmbedding(
            entity_id="doc_1",
            embedding=[0.1] * 1536,
            metadata={
                "user_id": "user_123",
                "category": "personal",
            },
        ),
        VectorEmbedding(
            entity_id="doc_2",
            embedding=[0.2] * 1536,
            metadata={
                "user_id": "user_456",
                "category": "work",
            },
        ),
    ]

    # Insert - partition key extracted from metadata
    await manager.insert(embeddings)
    print("✓ Inserted embeddings with user_id partition key")

    # Search for specific user
    query_vector = [0.15] * 1536
    results = await manager.search(
        query_vector=query_vector,
        k=10,
        partition_key="user_123",  # Search only user_123's data
    )
    print(f"✓ Found {len(results)} results for user_123")


if __name__ == "__main__":
    asyncio.run(main())


