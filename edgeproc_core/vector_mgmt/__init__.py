"""Vector partitioning and generic partition-key management.

Ships the partitioning protocol and an in-memory brute-force reference index —
HNSW ``m`` / ``ef_construction`` are pass-through knobs for downstream backends,
not an HNSW implementation shipped here.
"""

from importlib.metadata import PackageNotFoundError, version

from edgeproc_core.vector_mgmt.core.index_manager import IndexManager
from edgeproc_core.vector_mgmt.core.types import (
    IndexConfig,
    IndexStats,
    VectorEmbedding,
    VectorIndex,
)
from edgeproc_core.vector_mgmt.partitioning.strategies import (
    BucketedPartitionStrategy,
    GlobalPartitionStrategy,
    PartitionStrategy,
    TwoTierPartitionStrategy,
)

# Derived from the installed distribution metadata so it can never drift from
# pyproject.toml (the publish `sed` bumps only pyproject). Single source of truth.
try:
    __version__ = version("edgeproc-core")
except PackageNotFoundError:  # pragma: no cover - source checkout, not installed
    __version__ = "0.0.0+unknown"

__all__ = [
    "BucketedPartitionStrategy",
    "GlobalPartitionStrategy",
    "IndexConfig",
    "IndexManager",
    "IndexStats",
    "PartitionStrategy",
    "TwoTierPartitionStrategy",
    "VectorEmbedding",
    "VectorIndex",
]
