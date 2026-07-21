"""Composite-key demo: route by ``org_id:region`` via a custom extractor.

Sometimes a single metadata field isn't enough — you want per-org *and*
per-region isolation. Plug a ``partition_key_extractor`` callable into the
strategy; the rest of the API stays identical.
"""

from __future__ import annotations

import asyncio

from edgeproc_core import GlobalPartitionStrategy, IndexManager
from edgeproc_core.vector_mgmt.core.types import VectorEmbedding
from edgeproc_core.vector_mgmt.testing import in_memory_factory


def extract_org_region(emb: VectorEmbedding) -> str | None:
    """Build the composite key ``org_id:region`` from metadata."""
    org_id = emb.metadata.get("org_id")
    region = emb.metadata.get("region", "default")
    if isinstance(org_id, str):
        return f"{org_id}:{region}"
    return None


def _embed(
    entity_id: str,
    vector: list[float],
    org_id: str,
    region: str,
    category: str | None,
) -> VectorEmbedding:
    """Build a ``VectorEmbedding`` and pre-compute the composite key in metadata."""
    metadata: dict[str, str] = {
        "org_id": org_id,
        "region": region,
        "org_region": f"{org_id}:{region}",
    }
    if category is not None:
        metadata["category"] = category
    return VectorEmbedding(entity_id=entity_id, embedding=vector, metadata=metadata)


async def main() -> None:
    """Insert embeddings across two orgs and search a single org+region slice."""
    strategy = GlobalPartitionStrategy(
        index_factory=in_memory_factory,
        partition_key_name="org_region",
        partition_key_extractor=extract_org_region,
    )
    manager = IndexManager(
        partition_strategy=strategy,
        partition_key_name="org_region",
    )

    # The extractor partitions; the search filter still reads metadata by name,
    # so the composite key has to live in metadata too.
    embeddings = [
        _embed("entity_1", [0.1, 0.2, 0.3, 0.4], "org_123", "us-east", "documents"),
        _embed("entity_2", [0.5, 0.5, 0.5, 0.5], "org_123", "us-west", "images"),
        _embed("entity_3", [0.9, 0.8, 0.7, 0.6], "org_456", "eu-west", None),
    ]

    await manager.insert(embeddings)
    print(f"inserted {len(embeddings)} embeddings across org:region partitions")

    results = await manager.search(
        query_vector=[0.15, 0.25, 0.35, 0.45],
        k=10,
        partition_key="org_123:us-east",
    )
    print(f"top-{len(results)} matches for org_123:us-east:")
    for entity_id, distance in results:
        print(f"  {entity_id}  distance={distance:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
