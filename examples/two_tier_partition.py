"""End-to-end demo: hot/cold time-tiered routing, plus a maintenance rebuild.

`TwoTierPartitionStrategy` splits data by age. Recent rows go to a small "hot"
index that stays fast; older rows fall to a "cold" index you can keep on cheaper
storage. The split is read from each embedding's `metadata["created_at"]`, so
nothing has to be re-partitioned by hand as data ages.

A search spans both tiers and the manager merges the results, so callers never
have to know which tier a row lives in.

Uses the bundled ``InMemoryVectorIndex`` reference factory, so this runs cold
against a fresh checkout.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from edgeproc_core import IndexConfig, IndexManager, TwoTierPartitionStrategy
from edgeproc_core.vector_mgmt.core.types import VectorEmbedding
from edgeproc_core.vector_mgmt.testing import in_memory_factory

HOT_RETENTION_DAYS = 30


def _days_ago(days: int) -> str:
    """An ISO-8601 UTC timestamp ``days`` in the past."""
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def _catalogue() -> list[VectorEmbedding]:
    """Four rows straddling the 30-day hot/cold boundary."""
    ages = {"doc_today": 0, "doc_last_week": 7, "doc_last_quarter": 90, "doc_last_year": 365}
    return [
        VectorEmbedding(
            entity_id=entity_id,
            embedding=[0.1, 0.2, 0.3, 0.4],
            metadata={"tenant_id": "tenant_1", "created_at": _days_ago(days)},
        )
        for entity_id, days in ages.items()
    ]


async def main() -> None:
    """Route rows into hot/cold tiers, search across both, then run maintenance."""
    strategy = TwoTierPartitionStrategy(
        index_factory=in_memory_factory,
        hot_retention_days=HOT_RETENTION_DAYS,
        config=IndexConfig(dimension=4),
    )
    manager = IndexManager(partition_strategy=strategy)
    embeddings = _catalogue()

    tiers = strategy.get_partitions(embeddings)
    for tier in sorted(tiers):
        names = ", ".join(sorted(emb.entity_id for emb in tiers[tier]))
        print(f"{tier:>4} tier ({len(tiers[tier])}): {names}")

    await manager.insert(embeddings, partition_key="tenant_1")

    results = await manager.search([0.1, 0.2, 0.3, 0.4], k=10, partition_key="tenant_1")
    print(f"\nsearch spans both tiers — {len(results)} merged matches:")
    for entity_id, distance in results:
        print(f"  {entity_id:<18} distance={distance:.4f}")

    for stats in await manager.get_stats(partition_key="tenant_1"):
        print(f"stats: {stats.index_name:<11} {stats.vector_count} vectors")

    # Maintenance: rebuild the first tier that has drifted past its thresholds
    # (>10% tombstones or >1000 MB). `force=True` shows the call without having
    # to manufacture a degraded index first.
    rebuilt = await manager.rebuild_if_needed(partition_key="tenant_1", force=True)
    print(f"\nrebuild_if_needed(force=True) -> {rebuilt}")


if __name__ == "__main__":
    asyncio.run(main())
