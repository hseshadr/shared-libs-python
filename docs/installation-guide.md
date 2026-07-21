# Installation guide

**TL;DR.** `edgeproc-core` supports Python 3.13+ and is distributed from
the public GitHub repository. Pin the commit below:

```bash
uv pip install "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472"
```

That installs the real library. To see its complete partition-and-search path
against realistic in-memory data, clone the repository and run:

```bash
bash examples/run_loop.sh
```

## Requirements

- Python 3.13 or newer
- [`uv`](https://docs.astral.sh/uv/) (recommended) or `pip`

Create a clean environment with `uv`:

```bash
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate
```

## Install a pinned version

Pin a full commit SHA so a later commit cannot silently change an application's
dependency:

```bash
# uv
uv pip install "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472"

# pip
python -m pip install "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472"
```

For `pyproject.toml`:

```toml
[project]
requires-python = ">=3.13"
dependencies = [
  "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472",
]
```

For `requirements.txt`:

```text
edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472
```

### Why a commit and not a tag or a PyPI release?

`edgeproc-core` is not on PyPI yet, and the newest tag — `v0.2.0` — was cut
*before* the import package was renamed from `shared_libs_python` to
`edgeproc_core`. Installing that tag therefore succeeds but gives you the old
module name, and the verification snippet below would fail with
`ModuleNotFoundError: No module named 'edgeproc_core'`.

A full commit SHA is exactly as immutable as a tag — Git cannot repoint it — so
pinning one gives up nothing but brevity. The planned `0.3.0` release will
publish to PyPI and restore the short `pip install edgeproc-core` form.

## Verify the installation

```bash
python - <<'PY'
import edgeproc_core
from edgeproc_core import BucketedPartitionStrategy, VectorEmbedding

print(f"edgeproc-core {edgeproc_core.__version__}")
print(BucketedPartitionStrategy)
print(VectorEmbedding(entity_id="example", embedding=[0.1, 0.2]))
PY
```

Then follow the root [README quickstart](../README.md#60-second-quickstart) or
run the bundled end-to-end examples:

```bash
bash examples/run_loop.sh
```

## Development installs

Contributors should clone the repository so the lockfile and complete quality
gate are available:

```bash
git clone https://github.com/hseshadr/shared-libs-python.git
cd shared-libs-python
uv sync --all-extras --dev
uv run poe gate
```

Installing the moving `main` branch is intentionally a development-only path:

```bash
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@main
```

## Upgrade or reinstall

Change the pinned commit, then resynchronize the environment. For the currently
documented pin:

```bash
uv pip install --upgrade --force-reinstall \
  "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472"
```

## Troubleshooting

### Python version mismatch

If the resolver says the current interpreter does not satisfy Python 3.13,
create the environment explicitly:

```bash
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate
```

### Commit not found

Confirm the pinned commit exists on the public repository:

```bash
git ls-remote https://github.com/hseshadr/shared-libs-python.git | \
  grep 6cdf8475b223262821622a021c561aed9213a472
```

### `ModuleNotFoundError: No module named 'edgeproc_core'`

You almost certainly installed the `v0.2.0` tag rather than the pinned commit.
That tag predates the rename and ships the old `shared_libs_python` module.
Check what is actually installed and reinstall from the commit:

```bash
uv pip list | grep -i -E "edgeproc|shared"
```

### Cached older version

Prefer an explicit forced reinstall over clearing the entire shared `uv` cache:

```bash
uv pip install --upgrade --force-reinstall \
  "edgeproc-core @ git+https://github.com/hseshadr/shared-libs-python.git@6cdf8475b223262821622a021c561aed9213a472"
```

The supported release line and vulnerability-reporting process are documented
in [SECURITY.md](../SECURITY.md).
