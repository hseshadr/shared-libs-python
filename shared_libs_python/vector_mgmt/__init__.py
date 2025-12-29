"""Vector management package for HNSW indexing, partitioning, and generic partition key management."""

__version__ = "0.1.0"

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
]

