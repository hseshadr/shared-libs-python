"""Shared libraries for Python projects.

This package contains reusable libraries for various purposes.
Currently includes vector_mgmt for HNSW vector indexing and partitioning.
"""

__version__ = "0.1.0"

# Re-export vector_mgmt for backward compatibility and convenience
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

# Package exports
import shared_libs_python.vector_mgmt as vector_mgmt

__all__ = [
    "IndexManager",
    "PartitionStrategy",
    "GlobalPartitionStrategy",
    "BucketedPartitionStrategy",
    "TwoTierPartitionStrategy",
    "IndexConfig",
    "IndexStats",
    "VectorEmbedding",
    "VectorIndex",
    "vector_mgmt",
]

