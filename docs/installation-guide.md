# Installation guide

**TL;DR.** `shared-libs-python` supports Python 3.13+ and is distributed from
the public GitHub repository. Pin the latest released tag for applications:

```bash
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0
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

## Install a released version

Use the immutable Git tag so a later commit cannot silently change an
application's dependency:

```bash
# uv
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0

# pip
python -m pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0
```

The GitHub Release also contains a wheel:

```bash
uv pip install https://github.com/hseshadr/shared-libs-python/releases/download/v0.2.0/shared_libs_python-0.2.0-py3-none-any.whl
```

For `pyproject.toml`:

```toml
[project]
requires-python = ">=3.13"
dependencies = [
  "shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0",
]
```

For `requirements.txt`:

```text
shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0
```

## Verify the installation

```bash
python - <<'PY'
import shared_libs_python
from shared_libs_python import BucketedPartitionStrategy, VectorEmbedding

print(f"shared-libs-python {shared_libs_python.__version__}")
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

Change the pinned tag, then resynchronize the environment. For the current
release:

```bash
uv pip install --upgrade --force-reinstall \
  git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0
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

### Tag or artifact not found

Confirm the tag on the public repository:

```bash
git ls-remote --tags https://github.com/hseshadr/shared-libs-python.git
```

Released versions and artifacts are listed on the
[GitHub Releases page](https://github.com/hseshadr/shared-libs-python/releases).

### Cached older version

Prefer an explicit forced reinstall over clearing the entire shared `uv` cache:

```bash
uv pip install --upgrade --force-reinstall \
  git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0
```

The supported release line and vulnerability-reporting process are documented
in [SECURITY.md](../SECURITY.md).
