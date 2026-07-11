"""HNSW vector indexing, partitioning, and generic partition-key management."""

from importlib.metadata import PackageNotFoundError, version

from shared_libs_python.vector_mgmt.core.index_manager import IndexManager
from shared_libs_python.vector_mgmt.core.types import (
    IndexConfig,
    IndexStats,
    VectorEmbedding,
    VectorIndex,
)
from shared_libs_python.vector_mgmt.partitioning.strategies import (
    BucketedPartitionStrategy,
    GlobalPartitionStrategy,
    PartitionStrategy,
    TwoTierPartitionStrategy,
)

# Derived from the installed distribution metadata so it can never drift from
# pyproject.toml (the publish `sed` bumps only pyproject). Single source of truth.
try:
    __version__ = version("shared-libs-python")
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
