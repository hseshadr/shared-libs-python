# Installation Guide

This guide explains how to install `shared-libs-python` in your projects.

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- Access to the GitHub repository (for private repos)

## Installation Methods

### Method 1: From GitHub Release (Recommended)

Install a specific version directly from the GitHub Release artifacts:

```bash
# Using uv
uv pip install https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.0/shared_libs_python-0.1.0-py3-none-any.whl

# Using pip
pip install https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.0/shared_libs_python-0.1.0-py3-none-any.whl
```

### Method 2: From Git Tag

Install directly from a git tag:

```bash
# Using uv
uv pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.0

# Using pip
pip install git+https://github.com/hseshadr/shared-libs-python.git@v0.1.0
```

### Method 3: From Git Branch (Latest)

Install the latest from main branch:

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
dependencies = [
    "shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.1.0",
]
```

### Latest from Main Branch

```toml
[project]
dependencies = [
    "shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@main",
]
```

### From Release Artifact URL

```toml
[project]
dependencies = [
    "shared-libs-python @ https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.0/shared_libs_python-0.1.0-py3-none-any.whl",
]
```

## Adding to requirements.txt

```txt
# Pinned to tag
shared-libs-python @ git+https://github.com/hseshadr/shared-libs-python.git@v0.1.0

# Or from release artifact
shared-libs-python @ https://github.com/hseshadr/shared-libs-python/releases/download/v0.1.0/shared_libs_python-0.1.0-py3-none-any.whl
```

## Private Repository Access

If the repository is private, you need to configure authentication:

### Using SSH (Recommended)

```bash
# Ensure SSH key is configured with GitHub
uv pip install git+ssh://git@github.com/hseshadr/shared-libs-python.git@v0.1.0
```

In `pyproject.toml`:
```toml
dependencies = [
    "shared-libs-python @ git+ssh://git@github.com/hseshadr/shared-libs-python.git@v0.1.0",
]
```

### Using Personal Access Token

```bash
# Set token in environment
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Install with token
uv pip install git+https://${GITHUB_TOKEN}@github.com/hseshadr/shared-libs-python.git@v0.1.0
```

### In CI/CD (GitHub Actions)

```yaml
- name: Install private dependencies
  run: |
    uv pip install git+https://${{ secrets.GITHUB_TOKEN }}@github.com/hseshadr/shared-libs-python.git@v0.1.0
```

Or configure git credentials:

```yaml
- name: Configure git credentials
  run: |
    git config --global url."https://${{ secrets.GITHUB_TOKEN }}@github.com/".insteadOf "https://github.com/"

- name: Install dependencies
  run: |
    uv sync  # Will use git credentials for private deps
```

## Verifying Installation

```python
# Check version
import shared_libs_python
print(shared_libs_python.__version__)

# Verify imports work
from shared_libs_python import (
    IndexManager,
    GlobalPartitionStrategy,
    BucketedPartitionStrategy,
    TwoTierPartitionStrategy,
    IndexConfig,
    VectorEmbedding,
)

print("Installation successful!")
```

## Available Versions

Check the [Releases page](https://github.com/hseshadr/shared-libs-python/releases) for all available versions.

## Updating to a New Version

```bash
# Update to specific version
uv pip install --upgrade git+https://github.com/hseshadr/shared-libs-python.git@v0.2.0

# Or update pyproject.toml and re-sync
uv sync
```

## Troubleshooting

### Authentication Errors

If you see `403 Forbidden` or `Repository not found`:

1. Ensure you have access to the repository
2. Check your SSH key or token is valid
3. For tokens, ensure it has `repo` scope

### Version Not Found

If a version tag doesn't exist:

1. Check available tags: `git ls-remote --tags https://github.com/hseshadr/shared-libs-python.git`
2. Check the [Releases page](https://github.com/hseshadr/shared-libs-python/releases)

### Dependency Conflicts

If you encounter dependency conflicts:

```bash
# Show what's installed
uv pip list | grep shared

# Force reinstall
uv pip install --force-reinstall git+https://github.com/hseshadr/shared-libs-python.git@v0.1.0
```
