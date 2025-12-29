# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with 97.45% coverage
- GitHub Actions CI/CD workflow
- Contributing guidelines
- Security policy
- Issue templates
- Example implementations

## [0.1.0] - 2025-01-15

### Added
- Initial release of shared-libs-python
- Generic partition key support (tenant_id, user_id, org_id, etc.)
- Three partitioning strategies:
  - `GlobalPartitionStrategy`: Single global index with metadata filtering
  - `BucketedPartitionStrategy`: Hash-based bucketing for scale
  - `TwoTierPartitionStrategy`: Hot/cold tier separation
- `IndexManager` for coordinating vector indices
- `VectorIndex` protocol for abstract index interface
- Type-safe implementation with Pydantic models
- Backward compatibility with `tenant_id` field
- Custom partition key extractors support
- Comprehensive documentation

### Features
- Generic partition key extraction from metadata
- Support for any partition key name
- Composite partition keys via custom extractors
- Full type hints and mypy strict compliance
- Protocol-based design for extensibility

[Unreleased]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hseshadr/shared-libs-python/releases/tag/v0.1.0


