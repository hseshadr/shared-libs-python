"""The headline promise: nobody ever sees anyone else's results.

The README's central claim is that partitioning keeps tenants apart. Bucketing
makes collisions *inevitable* by design: once tenants outnumber buckets, two
tenants share one physical index. Proving isolation only on disjoint partitions
proves nothing about the case the design actually creates.

These tests force the worst case — ``num_buckets=1``, so every partition key
collides into a single index — and assert that a tenant-scoped read still
returns that tenant's rows and nothing else. Each isolation test is paired with
a non-vacuity assertion that the collision genuinely happened, so the suite can
never pass because the tenants quietly landed in separate buckets.
"""

from __future__ import annotations

import pytest

from shared_libs_python import BucketedPartitionStrategy, IndexManager
from shared_libs_python.vector_mgmt.core.types import VectorEmbedding
from shared_libs_python.vector_mgmt.testing import in_memory_factory

VECTOR = [0.1, 0.2, 0.3, 0.4]
"""One shared vector: every row is an equally good match, so only the partition
filter — never distance ranking — can be what keeps a tenant's rows out."""


def _embeddings(tenant: str, count: int, key_name: str = "tenant_id") -> list[VectorEmbedding]:
    """``count`` identically-embedded rows tagged for ``tenant``."""
    return [
        VectorEmbedding(entity_id=f"{tenant}-{i}", embedding=VECTOR, metadata={key_name: tenant})
        for i in range(count)
    ]


def _single_bucket(key_name: str = "tenant_id") -> BucketedPartitionStrategy:
    """A strategy whose every partition key collides into one physical index."""
    return BucketedPartitionStrategy(
        index_factory=in_memory_factory, num_buckets=1, partition_key_name=key_name
    )


def test_forced_collision_actually_puts_both_tenants_in_one_index() -> None:
    """Non-vacuity guard: the isolation tests below really do share an index."""
    strategy = _single_bucket()
    assert strategy.get_search_partitions("tenant_a") == strategy.get_search_partitions("tenant_b")

    partitions = strategy.get_partitions(_embeddings("tenant_a", 2) + _embeddings("tenant_b", 2))

    assert len(partitions) == 1, "expected one shared bucket, got a disjoint split"
    assert len(next(iter(partitions.values()))) == 4


@pytest.mark.parametrize(("mine", "theirs"), [("tenant_a", "tenant_b"), ("tenant_b", "tenant_a")])
async def test_search_under_forced_collision_returns_only_the_querying_tenant(
    mine: str, theirs: str
) -> None:
    """Colliding tenants share one index; a scoped search still sees only its own."""
    manager = IndexManager(partition_strategy=_single_bucket())
    await manager.insert(_embeddings(mine, 3))
    await manager.insert(_embeddings(theirs, 3))

    results = await manager.search(VECTOR, k=10, partition_key=mine)
    returned = {entity_id for entity_id, _ in results}

    assert returned == {f"{mine}-0", f"{mine}-1", f"{mine}-2"}
    assert not any(entity_id.startswith(theirs) for entity_id in returned)


async def test_search_under_forced_collision_isolates_a_custom_partition_key() -> None:
    """Isolation is a property of the partition key, not of the name ``tenant_id``."""
    manager = IndexManager(
        partition_strategy=_single_bucket("user_id"), partition_key_name="user_id"
    )
    await manager.insert(_embeddings("user_a", 2, "user_id"))
    await manager.insert(_embeddings("user_b", 2, "user_id"))

    returned = {
        entity_id for entity_id, _ in await manager.search(VECTOR, k=10, partition_key="user_a")
    }

    assert returned == {"user_a-0", "user_a-1"}


async def test_collision_does_not_shadow_rows_that_share_an_entity_id_prefix() -> None:
    """A colliding neighbour cannot displace a tenant's own rows from its top-k."""
    manager = IndexManager(partition_strategy=_single_bucket())
    await manager.insert(_embeddings("tenant_a", 2))
    await manager.insert(_embeddings("tenant_b", 50))

    returned = await manager.search(VECTOR, k=2, partition_key="tenant_a")

    assert {entity_id for entity_id, _ in returned} == {"tenant_a-0", "tenant_a-1"}


async def test_an_unscoped_search_is_explicitly_not_isolated() -> None:
    """The stated boundary: isolation comes from the partition key the caller passes.

    Searching with ``partition_key=None`` applies no filter and is documented as
    an administrative, cross-tenant read. Pinning it here keeps the promise
    honest — the library isolates *scoped* reads, and never claims to guess
    scope the caller did not supply.
    """
    manager = IndexManager(partition_strategy=_single_bucket())
    await manager.insert(_embeddings("tenant_a", 2))
    await manager.insert(_embeddings("tenant_b", 2))

    returned = {entity_id for entity_id, _ in await manager.search(VECTOR, k=10)}

    assert len(returned) == 4
