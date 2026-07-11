"""Shared libraries for Python projects.

This package contains reusable libraries for various purposes.
Currently includes vector_mgmt for vector partitioning and generic
partition-key management.
"""

from importlib.metadata import PackageNotFoundError, version

# Re-export vector_mgmt for backward compatibility and convenience
# Package exports
from shared_libs_python import vector_mgmt
from shared_libs_python.vector_mgmt import (
    BucketedPartitionStrategy,
    GlobalPartitionStrategy,
    IndexConfig,
    IndexManager,
    IndexStats,
    PartitionStrategy,
    TwoTierPartitionStrategy,
    VectorEmbedding,
    VectorIndex,
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
    "vector_mgmt",
]
