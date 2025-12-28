# shared-libs-python

Shared library for HNSW vector indexing, partitioning, and generic partition key management.

## Features

- **Generic partitioning strategies**: Global, bucketed, two-tier (hot/cold) - works with any partition key
- **Flexible partition keys**: Support for tenant_id, user_id, org_id, or any custom partition key
- **Index management**: Abstract interface for vector indices
- **Reindexing utilities**: Background rebuild + atomic swap patterns
- **Type-safe**: Full Pydantic models, type hints, protocol-based design

## Installation

```bash
cd ~/dev/shared-libs-python
uv sync
uv pip install -e .
```

Or install from other projects:

```bash
# In your project
uv pip install -e ~/dev/shared-libs-python
```

## Usage

### Basic Usage with tenant_id (Backward Compatible)

```python
from shared_libs_python import IndexManager, GlobalPartitionStrategy, IndexConfig
from shared_libs_python.core.types import VectorEmbedding

# Create index factory (implement VectorIndex protocol)
async def create_index(name: str, config: IndexConfig):
    # Return your VectorIndex implementation
    ...

# Setup partition strategy (defaults to tenant_id)
strategy = GlobalPartitionStrategy(
    index_factory=create_index,
    index_name="global",
    config=IndexConfig(m=32, ef_construction=200),
)

# Create manager
manager = IndexManager(partition_strategy=strategy)

# Insert embeddings
embeddings = [
    VectorEmbedding(
        entity_id="entity_1",
        embedding=[0.1, 0.2, ...],
        tenant_id="tenant_1",  # Still supported for backward compatibility
    )
]
await manager.insert(embeddings, partition_key="tenant_1")

# Search
results = await manager.search(
    query_vector=[0.1, 0.2, ...],
    k=10,
    partition_key="tenant_1",
)
```

### Using Custom Partition Keys

```python
# Example: User-based partitioning
strategy = BucketedPartitionStrategy(
    index_factory=create_index,
    num_buckets=256,
    partition_key_name="user_id",  # Use user_id instead of tenant_id
)

manager = IndexManager(
    partition_strategy=strategy,
    partition_key_name="user_id",
)

# Embeddings with user_id in metadata
embeddings = [
    VectorEmbedding(
        entity_id="entity_1",
        embedding=[0.1, 0.2, ...],
        metadata={"user_id": "user_123", "category": "documents"},
    )
]
await manager.insert(embeddings, partition_key="user_123")

# Search for a specific user
results = await manager.search(
    query_vector=[0.1, 0.2, ...],
    k=10,
    partition_key="user_123",
)
```

### Using Custom Partition Key Extractor

```python
# Example: Composite partition key (org_id + region)
def extract_partition_key(emb: VectorEmbedding) -> str | None:
    org_id = emb.metadata.get("org_id")
    region = emb.metadata.get("region", "default")
    if org_id:
        return f"{org_id}:{region}"
    return None

strategy = GlobalPartitionStrategy(
    index_factory=create_index,
    partition_key_name="org_region",
    partition_key_extractor=extract_partition_key,
)
```

## Partitioning Strategies

All strategies support generic partition keys via the `partition_key_name` parameter.

### GlobalPartitionStrategy
Single global index with metadata filtering. Best for < 50K partition keys.

**Parameters:**
- `partition_key_name`: Name of partition key (default: "tenant_id")
- `partition_key_extractor`: Optional custom function to extract partition key

### BucketedPartitionStrategy
Hash-based bucketing (e.g., 256 buckets). Best for 50K - 5M partition keys.

**Parameters:**
- `num_buckets`: Number of buckets (default: 256)
- `partition_key_name`: Name of partition key (default: "tenant_id")
- `partition_key_extractor`: Optional custom function to extract partition key

### TwoTierPartitionStrategy
Hot/cold separation for recent vs historical data based on `created_at` metadata.

**Parameters:**
- `hot_retention_days`: Days to keep in hot tier (default: 30)
- `partition_key_name`: Name of partition key (default: "tenant_id")
- `partition_key_extractor`: Optional custom function to extract partition key

## Migration from tenant_id to Generic Partition Keys

The library now supports generic partition keys while maintaining backward compatibility:

**Backward Compatible:**
- `VectorEmbedding.tenant_id` field still works
- Default `partition_key_name="tenant_id"` maintains existing behavior
- Old code using `tenant_id` parameter will continue to work

**New Generic API:**
- Use `partition_key` parameter instead of `tenant_id` in `IndexManager` methods
- Configure `partition_key_name` in strategies for custom keys
- Store partition keys in `metadata` dict for flexibility

**Example Migration:**
```python
# Old API (still works)
await manager.insert(embeddings, tenant_id="tenant_1")
await manager.search(query_vector, k=10, tenant_id="tenant_1")

# New Generic API (recommended)
await manager.insert(embeddings, partition_key="tenant_1")
await manager.search(query_vector, k=10, partition_key="tenant_1")
```

## Development

```bash
# Run tests
uv run pytest

# Type checking
uv run mypy shared_libs_python

# Linting
uv run ruff check .
```

## License

MIT

