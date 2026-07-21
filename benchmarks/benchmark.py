"""Repeatable release benchmark for library-owned routing and reference search."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from time import perf_counter

from shared_libs_python.vector_mgmt.core.types import VectorEmbedding
from shared_libs_python.vector_mgmt.partitioning.strategies import BucketedPartitionStrategy
from shared_libs_python.vector_mgmt.testing import InMemoryVectorIndex, in_memory_factory

ENTITY_COUNT = 10_000
DIMENSION = 32
RUNS = 20
PARTITION_P50_MS = 100.0
PARTITION_P95_MS = 200.0
SEARCH_P50_MS = 500.0
SEARCH_P95_MS = 750.0


def _percentile(samples: list[float], rank: float) -> float:
    ordered = sorted(samples)
    return ordered[max(0, int(len(ordered) * rank + 0.9999) - 1)]


def _timed(call: Callable[[], object]) -> float:
    started = perf_counter()
    call()
    return (perf_counter() - started) * 1000.0


def _embeddings(dimension: int) -> list[VectorEmbedding]:
    vector = [1.0 / dimension**0.5] * dimension
    return [
        VectorEmbedding(entity_id=str(i), embedding=vector, metadata={"tenant_id": f"t{i}"})
        for i in range(ENTITY_COUNT)
    ]


def _partition_samples(embeddings: list[VectorEmbedding]) -> list[float]:
    strategy = BucketedPartitionStrategy(in_memory_factory, num_buckets=256)
    strategy.get_partitions(embeddings)
    return [_timed(lambda: strategy.get_partitions(embeddings)) for _ in range(RUNS)]


async def _search_samples(embeddings: list[VectorEmbedding]) -> list[float]:
    index = InMemoryVectorIndex("benchmark")
    await index.insert(embeddings)
    query = embeddings[0].embedding
    await index.search(query, 10)
    return [await _timed_search(index, query) for _ in range(RUNS)]


async def _timed_search(index: InMemoryVectorIndex, query: list[float]) -> float:
    started = perf_counter()
    await index.search(query, 10)
    return (perf_counter() - started) * 1000.0


def _report(label: str, samples: list[float]) -> tuple[float, float]:
    p50 = _percentile(samples, 0.50)
    p95 = _percentile(samples, 0.95)
    print(f"{label}: p50={p50:.1f}ms p95={p95:.1f}ms runs={RUNS}")
    return p50, p95


def main() -> None:
    routed = _embeddings(8)
    searched = _embeddings(DIMENSION)
    route_p50, route_p95 = _report("partition", _partition_samples(routed))
    search_p50, search_p95 = _report("reference-search", asyncio.run(_search_samples(searched)))
    assert route_p50 <= PARTITION_P50_MS and route_p95 <= PARTITION_P95_MS
    assert search_p50 <= SEARCH_P50_MS and search_p95 <= SEARCH_P95_MS


if __name__ == "__main__":
    main()
