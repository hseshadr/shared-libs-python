# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] — 2026-07-20

### Added
- **Distinguished-engineer operating contract and repeatable benchmark.**
  `docs/OPERATIONS.md` now makes the package's trust, privacy, recovery, and
  performance ownership explicit; `benchmarks/northstar.py` records fixed
  p50/p95 budgets for 10,000-item routing and the in-memory reference search.
- **`shared_libs_python.errors` — canonical errors module.** The Python mirror
  of the `@edgeproc/errors` TS package, so a failure carries the same stable
  code and RFC 9457 shape on both sides of the portfolio. An app registers its
  own catalog with `define_errors(...)`, classifies a raw transport/LLM failure
  into one of its codes (`Registry.classify`), describes it through its own
  i18n with the catalog English as fallback (`Registry.describe`), and
  serializes to Problem Details (`Registry.to_problem_details` → the frozen
  `ProblemDetails` dataclass). The optional `starter_pack` supplies 18 universal
  codes (provider/config/network/timeout/device/integrity/internal) so a site
  need not re-declare the common ones. Duplicate codes raise `DuplicateCodeError`
  at registration. Public surface: `define_errors`, `Registry`, `starter_pack`,
  `ProblemDetails`, `Catalog`/`CatalogEntry`/`Category`/`ErrorCode`/`MatchRule`/
  `Params`/`ParamValue`/`TFunction`, `CanonicalError`, and the raw helpers
  `http_status_of`/`error_name_of`/`error_text_of`. Additive — no change to any
  existing module; this is the minor-version feature behind a 0.2.0 tag.

### Changed
- **Public status now matches the released `0.2.0` package.** README install
  examples and `SECURITY.md` supported-version policy no longer point at the
  stale `0.1.4`/`0.1.x` line; production-backend targets are labeled as
  consumer guidance rather than library SLA claims.
- **Workflow actions are immutable.** CI, security audit, artifact handoff,
  Codecov, gitleaks, and GitHub release actions are pinned to full commit SHAs,
  with a regression test that rejects moving tags.

### Fixed
- **Invalid bucket counts now fail at construction.**
  `BucketedPartitionStrategy` rejects zero and negative `num_buckets` values at
  the public boundary instead of failing later during routing with a modulo
  error or producing invalid negative bucket identifiers.

## [0.1.4] — 2026-07-13

### Changed
- **`IndexConfig.distance_metric` is now a typed literal, not a bare string.**
  The field was `str = "cosine"` with a `# cosine, l2, inner_product` comment
  carrying the invariant. It is now `Literal["cosine", "l2", "inner_product"]`
  (exposed as the `DistanceMetric` alias), so Pydantic rejects an unsupported
  metric at construction and `mypy` catches an invalid literal statically.
  Public behavior for the three documented metrics is unchanged.
- **Releases now require the full quality gate.** The publish workflow's
  `test` job ran pytest only and gated nothing — a tag push could publish
  even with failing checks. It is replaced by a `gate` job that mirrors CI
  (`uv run poe gate`: ruff lint, format check, mypy strict, xenon A, pytest
  with ≥90% coverage), and both `build` and `release` `needs:` it. Nothing
  publishes unless the gate passes on the tagged commit.

### Fixed
- **Timezone-aware `created_at` timestamps no longer raise `TypeError`.**
  `TwoTierPartitionStrategy` compared parsed timestamps against a naive
  cutoff, so any aware timestamp (e.g. a `Z` or `+00:00` suffix — the common
  case for stored ISO-8601) crashed classification. The contract is now
  explicit: all comparisons happen in UTC; both aware and naive `created_at`
  values are accepted, and naive values are interpreted as UTC. The lenient
  edges are unchanged (missing → hot, malformed → cold).
- **Two-tier rebuild no longer crashes.** `IndexManager.rebuild_if_needed`
  routed rebuilds by `stats.index_name` ("hot_index"/"cold_index"), which
  `TwoTierPartitionStrategy.get_index` rejects — it only accepts the
  partition names "hot"/"cold" — so any two-tier rebuild raised `ValueError`.
  Rebuilds now iterate partition names and pair each index with its own
  stats, which is correct for every strategy regardless of how it names the
  indexes it hands to the factory.
- **Concurrent lazy index creation no longer loses writes.** All three
  partition strategies raced on first access: two concurrent `get_index`
  calls could each create an index, with the loser's instance (and any writes
  applied to it) silently replaced. Creation is now guarded by an
  `asyncio.Lock` with a double-checked fast path — the factory runs exactly
  once per partition and every concurrent caller receives the same instance.
- **`BucketedPartitionStrategy` routing is now actually deterministic.** Bucket
  ids are computed from a SHA-256 digest of the UTF-8 encoded partition key
  instead of Python's builtin `hash()`, which is randomized per process
  (PYTHONHASHSEED). **Breaking-behavior note:** bucket assignments change for
  anyone who persisted them — but prior assignments were already unstable
  across processes (every restart could re-route every key), so this is
  strictly a fix. Re-partition persisted data once on upgrade; assignments are
  now stable across processes, machines, and Python versions.

## [0.1.3] — 2026-07-11

Standards-alignment release — Wave-0 pilot of the portfolio house standard
(`ENGINEERING-STANDARDS.md`). No library code changes; the public API is
identical to 0.1.2.

### Changed
- Renamed the composite quality task `poe quality` → `poe gate` and added the
  missing `ruff format --check` step (as `poe fmt-check`), so the local gate
  mirrors CI exactly in both directions. No `poe quality` alias kept.
- CI now runs `uv run poe gate` directly. Previously the xenon complexity step
  ran only locally and the format check ran only in CI — both one-sided drifts
  are gone.
- Bumped CI actions to the house floor: `actions/checkout@v5`,
  `actions/setup-python@v6`, `astral-sh/setup-uv@v8`,
  `codecov/codecov-action@v5`.
- Restructured the README into the two-altitude shape: plain-language front
  door, technical depth under "Under the hood (for developers)".
- Dev-dependency security fixes from the first pip-audit run:
  pygments → 2.20.0 (CVE-2026-4539), pytest → 9.1.1 (PYSEC-2026-1845);
  replaced yanked numpy 2.4.0 → 2.5.1.

### Added
- Full-history gitleaks secret-scan job in CI (`gitleaks/gitleaks-action@v3`).
- Weekly `security-audit.yml` workflow running pip-audit over the locked
  dependency export.
- `.github/dependabot.yml` — weekly, grouped updates for GitHub Actions and
  the uv lockfile.
- `CLAUDE.md`: "Quality Gates (Non-Negotiable)" section with scars, and the
  house-standard §8 WASM/edge-compute N/A declaration.

## [0.1.2] — 2026-06-19

Public open-source release (MIT). Part of the `edge-reco → edge-proc →
shared-libs-python` stack going public together; live demo at https://edge-reco.com.

### Added
- `shared_libs_python.vector_mgmt.testing` — `InMemoryVectorIndex` reference
  implementation and `in_memory_factory`, so the bundled `examples/` run
  end-to-end against a fresh checkout.
- `examples/run_loop.sh` — single-command end-to-end demo walking all three
  examples.

### Changed
- README cross-links the three-repo stack and states its role (the
  vector-partitioning protocol edge-proc's FAISS runtime builds on).
- Root `README.md` rewritten for cold-reader clarity: 4-part TL;DR, ≤15-line
  teaser quickstart, source-tree diagram aligned to the actual layout.
- `examples/basic_usage.py`, `custom_partition_key.py`,
  `composite_partition_key.py` now use the bundled in-memory factory and
  produce real output (previously crashed with `NoneType has no attribute
  'insert'`).
- `CLAUDE.md`: dropped stale "Placeholder Modules" section
  (`vector_mgmt/indexing/`, `vector_mgmt/reindex/` were removed in v0.1.1);
  documented the `testing` module; fixed `metadata: dict[str, Any]` to
  `dict[str, Scalar]`.

### Removed
- Stale root-level review documents (`PROJECT_REVIEW.md`, `GITHUB_REVIEW.md`,
  `REVIEW_SUMMARY.md`) from the pre-v0.1.1 review cycle.

## [0.1.1] - 2026-05-21

### Changed
- Tightened the entire public surface to the strict python-quality bar: `mypy --strict` clean, Radon Grade A complexity (cyclomatic ≤ 5), all functions ≤ 15 lines, no `Dict[str, Any]` in user code.
- Replaced ad-hoc `dict[str, Any]` metadata/filter types with a `Scalar` / `Metadata` type alias pair (`Scalar = str | int | float | bool | None`).
- Introduced `IndexFactory` Protocol replacing the previous `Callable[..., Awaitable[VectorIndex]]` annotation.
- `IndexManager.search` refactored into `_compose_filters` + `_merge_top_k` helpers (Grade A).
- `TwoTierPartitionStrategy.get_partitions` refactored into a `_classify_embedding` helper (Grade A). Behavior preserved (naive `datetime.now()`; missing/non-string `created_at` → hot; parse error → cold).
- Magic-number thresholds in `IndexManager.rebuild_if_needed` named with `Final[float]`.
- Moved unused runtime extras (`pgvector`, `sqlalchemy[asyncio]`, `numpy`) from required dependencies to `[project.optional-dependencies].pgvector`. Default install is now lean (pydantic only).
- Added `poe` tasks: `lint`, `fmt`, `typecheck`, `complexity`, `test`, `quality`.
- Updated `pyproject.toml` author from "Vector Management Team" to "Harish Seshadri".

### Removed
- Empty `shared_libs_python.vector_mgmt.indexing` and `shared_libs_python.vector_mgmt.reindex` submodules (referenced nothing; no public symbols exported).
- "Reindexing utilities" feature claim from the README.

### Added
- `xenon`, `radon`, `poethepoet` as dev dependencies for the strict quality gate.

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

[Unreleased]: https://github.com/hseshadr/shared-libs-python/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.4...v0.2.0
[0.1.4]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/hseshadr/shared-libs-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/hseshadr/shared-libs-python/releases/tag/v0.1.0
