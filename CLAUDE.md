# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Install dependencies
uv sync
uv pip install -e .

# Run all tests (includes coverage, requires 90%+)
uv run pytest

# Run specific test file
uv run pytest tests/test_types.py

# Run specific test method
uv run pytest tests/test_index_manager.py::TestIndexManager::test_insert

# Type checking (strict mode)
uv run mypy shared_libs_python

# Linting
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .
```

## Architecture Overview

This library provides HNSW vector index management with flexible partitioning strategies. Core principle: do NOT create one index per tenant—use global or bucketed indices with metadata filtering.

![Architecture Diagram](docs/diagrams/architecture.svg)

### Public API

```python
from shared_libs_python import (
    IndexManager,
    PartitionStrategy, GlobalPartitionStrategy, BucketedPartitionStrategy, TwoTierPartitionStrategy,
    IndexConfig, IndexStats, VectorEmbedding, VectorIndex,
)
```

### Core Types (`vector_mgmt/core/types.py`)

**VectorEmbedding**: Pydantic model for vectors.
- `entity_id`, `embedding: list[float]`, `metadata: dict[str, Any]`
- `tenant_id`: Deprecated—use `metadata["tenant_id"]` instead
- `get_partition_key(key_name)`: Resolves from metadata, falls back to `tenant_id`

**IndexConfig**: HNSW parameters.
- `m=32`: Graph connectivity (higher = better recall, more memory)
- `ef_construction=200`: Build-time search depth
- `ef_search=100`: Query-time search depth
- `dimension=1536`, `distance_metric="cosine"`

**IndexStats**: Index health metrics. Key fields: `tombstone_percentage`, `index_size_mb`.

**VectorIndex Protocol**: Interface for vector DB implementations.
- `insert(embeddings)`, `delete(entity_ids)`, `rebuild(config)`
- `search(query_vector, k, filters, ef_search)` → `list[(entity_id, distance)]` (lower distance = more similar)
- `get_stats()` → `IndexStats`

### IndexManager (`vector_mgmt/core/index_manager.py`)

Orchestrates vector operations: `insert()`, `search()`, `delete()`, `get_stats()`, `rebuild_if_needed()`.

`rebuild_if_needed()` auto-triggers when: tombstone_percentage > 10% OR index_size_mb > 1000.

### Partitioning Strategies (`vector_mgmt/partitioning/strategies.py`)

All inherit from `PartitionStrategy` ABC with `partition_key_name` and `partition_key_extractor` options.

| Strategy | Scale | Behavior |
|----------|-------|----------|
| GlobalPartitionStrategy | <50K keys | Single index, metadata filtering |
| BucketedPartitionStrategy | 50K-5M keys | Hash routing to N buckets (default 256) |
| TwoTierPartitionStrategy | Time-based | Hot/cold split on `created_at` metadata |

### Key Design Pattern: Index Factory

```python
async def factory(name: str, config: IndexConfig) -> VectorIndex:
    return YourVectorIndexImpl(name, config)

strategy = GlobalPartitionStrategy(index_factory=factory, ...)
```

### Placeholder Modules

`vector_mgmt/indexing/` and `vector_mgmt/reindex/` are stubs for future index implementations and atomic-swap reindexing.

## Testing

Tests use `MockVectorIndex` from `tests/conftest.py`—an in-memory `VectorIndex` implementation.

Key fixtures: `mock_index_factory`, `sample_embeddings`, `index_config`.

## Examples

See `examples/` for usage patterns: `basic_usage.py`, `custom_partition_key.py`, `composite_partition_key.py`.

## Dependencies

Core: `pydantic>=2.5`, `numpy>=1.26`, `sqlalchemy[asyncio]>=2.0`, `pgvector>=0.2.4`

## Code Style

- Line length: 100 chars
- Python 3.13+ type hints (`list[T]` not `List[T]`)
- Google-style docstrings
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`

## Reference Docs

- `docs/vector-mgmt-architecture.md`: Deep dive on partitioning rationale and scaling guidelines (note: some sections describe planned features)
