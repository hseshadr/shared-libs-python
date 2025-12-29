"""Example using composite partition keys (org_id + region)."""

import asyncio

from shared_libs_python import GlobalPartitionStrategy, IndexConfig, IndexManager
from shared_libs_python.vector_mgmt.core.types import VectorEmbedding


async def create_mock_index(name: str, config: IndexConfig | None = None) -> None:
    """Mock index factory."""
    _ = config  # Unused in mock implementation
    print(f"Creating index: {name}")


def extract_org_region(emb: VectorEmbedding) -> str | None:
    """Custom extractor for composite partition key: org_id:region."""
    org_id = emb.metadata.get("org_id")
    region = emb.metadata.get("region", "default")
    if org_id:
        return f"{org_id}:{region}"
    return None


async def main() -> None:
    """Example with composite partition key."""
    # Setup strategy with custom partition key extractor
    strategy = GlobalPartitionStrategy(
        index_factory=create_mock_index,
        partition_key_name="org_region",
        partition_key_extractor=extract_org_region,
    )

    manager = IndexManager(
        partition_strategy=strategy,
        partition_key_name="org_region",
    )

    # Embeddings with org_id and region
    embeddings = [
        VectorEmbedding(
            entity_id="entity_1",
            embedding=[0.1] * 1536,
            metadata={
                "org_id": "org_123",
                "region": "us-east",
                "category": "documents",
            },
        ),
        VectorEmbedding(
            entity_id="entity_2",
            embedding=[0.2] * 1536,
            metadata={
                "org_id": "org_123",
                "region": "us-west",
                "category": "images",
            },
        ),
        VectorEmbedding(
            entity_id="entity_3",
            embedding=[0.3] * 1536,
            metadata={
                "org_id": "org_456",
                "region": "eu-west",
            },
        ),
    ]

    # Insert - composite keys extracted automatically
    await manager.insert(embeddings)
    print("✓ Inserted embeddings with composite partition keys")

    # Search for specific org:region
    query_vector = [0.15] * 1536
    results = await manager.search(
        query_vector=query_vector,
        k=10,
        partition_key="org_123:us-east",  # Search only this org:region
    )
    print(f"✓ Found {len(results)} results for org_123:us-east")


if __name__ == "__main__":
    asyncio.run(main())
