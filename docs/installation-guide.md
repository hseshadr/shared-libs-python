# Installation Guide

This guide explains how to install `shared-libs-python` in your projects.

## Prerequisites

- **Python 3.13+** (required - the package will not install on older versions)
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Access to the GitHub repository (for private repos)

## Quick Start

```bash
# Ensure you have Python 3.13+
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate

# Install from git tag (recommended for private repos)
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

## Installation Methods

### Method 1: From Git Tag (Recommended)

This is the **recommended method for private repositories** as it uses your local git credentials automatically.

```bash
# Using uv
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2

# Using pip
pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### Method 2: From GitHub Release Artifact

> **Note:** Direct wheel URLs return 404 for private repositories. Use Method 1 (git tag) instead for private repos.

For **public repositories only**:

```bash
# Using uv
uv pip install https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.2/shared_libs_python-0.1.2-py3-none-any.whl

# Using pip
pip install https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.2/shared_libs_python-0.1.2-py3-none-any.whl
```

### Method 3: From Git Branch (Latest)

Install the latest from main branch (useful for development):

```bash
# Using uv
uv pip install git+https://github.com/hseshadr/shared-libs-python.git

# Using pip
pip install git+https://github.com/hseshadr/shared-libs-python.git
```

## Adding to pyproject.toml

### Pinned Version (Recommended for Production)

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2",
]
```

### Latest from Main Branch

```toml
[project]
dependencies = [
    "shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@main",
]
```

## Adding to requirements.txt

```txt
# Pinned to tag (recommended)
shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

## Private Repository Access

Since this is a private repository, you need proper authentication configured.

### Method A: HTTPS with Git Credential Helper (Simplest)

If you've already authenticated with GitHub via `gh auth login` or git credential helper, `git+https://` URLs will work automatically:

```bash
# This uses your cached git credentials
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### Method B: SSH (Recommended for CI/CD)

```bash
# Ensure SSH key is configured with GitHub
uv pip install git+ssh://git@github.com/hseshadr/shared-libs-python.git@v0.1.2
```

In `pyproject.toml`:
```toml
dependencies = [
    "shared-libs-python @ git+ssh://git@github.com/hseshadr/shared-libs-python.git@v0.1.2",
]
```

### Method C: Personal Access Token

```bash
# Set token in environment
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Install with token embedded in URL
uv pip install git+https://${GITHUB_TOKEN}@github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### In CI/CD (GitHub Actions)

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.13
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Configure git credentials for private deps
        run: |
          git config --global url."https://${{ secrets.GITHUB_TOKEN }}@github.com/".insteadOf "https://github.com/"

      - name: Install dependencies
        run: |
          uv sync
```

Or install directly with token:

```yaml
- name: Install private dependencies
  run: |
    uv pip install git+https://${{ secrets.GITHUB_TOKEN }}@github.com/hseshadr/shared-libs-python.git@v0.1.2
```

## Verifying Installation

```python
# Check version
import shared_libs_python
print(f"Version: {shared_libs_python.__version__}")

# Verify imports work
from shared_libs_python import (
    IndexManager,
    GlobalPartitionStrategy,
    BucketedPartitionStrategy,
    TwoTierPartitionStrategy,
    IndexConfig,
    VectorEmbedding,
)

# Test creating objects
config = IndexConfig(m=16, ef_construction=100)
emb = VectorEmbedding(entity_id="test", embedding=[0.1, 0.2, 0.3])

print("Installation successful!")
```

## Available Versions

Check the [Releases page](https://github.com/hseshadr/shared-libs-python/releases) for all available versions.

| Version | Release Date | Notes |
|---------|--------------|-------|
| v0.1.2  | 2025-12-29   | Initial release |

## Updating to a New Version

```bash
# Update to specific version
uv pip install --upgrade git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0

# Or update pyproject.toml version and re-sync
uv sync
```

## Troubleshooting

### Python Version Error

```
Because the current Python version (3.12.x) does not satisfy Python>=3.13
```

**Solution:** This package requires Python 3.13+. Create a venv with Python 3.13:

```bash
uv python install 3.13
uv venv --python 3.13
source .venv/bin/activate
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### 404 Not Found on Wheel URL

```
HTTP status client error (404 Not Found) for url
```

**Solution:** Direct wheel URLs don't work for private repositories. Use git+https instead:

```bash
# Instead of this (fails for private repos):
uv pip install https://github.com/.../shared_libs_python-0.1.2-py3-none-any.whl

# Use this:
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### Authentication Errors

```
403 Forbidden
Repository not found
```

**Solutions:**
1. Ensure you have access to the repository
2. Authenticate with GitHub: `gh auth login`
3. Check your SSH key: `ssh -T git@github.com`
4. For tokens, ensure it has `repo` scope

### Version/Tag Not Found

```
fatal: couldn't find remote ref refs/tags/v0.1.2
```

**Solutions:**
1. Check available tags:
   ```bash
   git ls-remote --tags https://github.com/hseshadr/shared-libs-python.git
   ```
2. Check the [Releases page](https://github.com/hseshadr/shared-libs-python/releases)

### Dependency Conflicts

```bash
# Show what's installed
uv pip list | grep shared

# Force reinstall
uv pip install --force-reinstall git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```

### Cache Issues

If you're getting stale versions:

```bash
# Clear uv cache
uv cache clean

# Reinstall
uv pip install --no-cache git+https://github.com/hseshadr/shared-libs-python.git@v0.1.2
```
