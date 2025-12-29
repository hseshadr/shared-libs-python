# Contributing to shared-libs-python

Thank you for your interest in contributing to shared-libs-python! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/hseshadr/shared-libs-python.git
cd shared-libs-python

# Install dependencies
uv sync
uv pip install -e .
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clean, type-safe code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=shared_libs_python --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_types.py
```

### 4. Type Checking

```bash
uv run mypy shared_libs_python
```

### 5. Linting

```bash
# Check for linting issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

### 6. Commit Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add new partition strategy"
git commit -m "fix: correct type hint in IndexManager"
git commit -m "docs: update README with examples"
git commit -m "test: add tests for custom extractors"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Type Hints

- All functions must have type hints
- Use `mypy --strict` compliance
- Prefer `list[T]` over `List[T]` (Python 3.9+)
- Use `dict[str, Any]` instead of `Dict[str, Any]`

### Code Formatting

- Line length: 100 characters
- Use `ruff` for formatting and linting
- Follow existing code patterns

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include type information in docstrings

## Testing Requirements

### Coverage

- Maintain **90%+ code coverage**
- All new code must have tests
- Edge cases should be covered

### Test Structure

- Unit tests in `tests/` directory
- Use descriptive test names: `test_function_name_scenario`
- Use fixtures from `conftest.py` when possible

### Running Tests

```bash
# All tests
uv run pytest

# With coverage report
uv run pytest --cov=shared_libs_python --cov-report=html

# Specific test
uv run pytest tests/test_index_manager.py::TestIndexManager::test_insert
```

## Pull Request Process

1. **Update CHANGELOG.md** with your changes
2. **Ensure all tests pass** (`uv run pytest`)
3. **Ensure type checking passes** (`uv run mypy shared_libs_python`)
4. **Ensure linting passes** (`uv run ruff check .`)
5. **Update documentation** if needed
6. **Request review** from maintainers

### PR Checklist

- [ ] Tests added/updated
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Coverage maintained at 90%+

## Adding New Features

### Partition Strategies

If adding a new partition strategy:

1. Extend `PartitionStrategy` base class
2. Implement required abstract methods
3. Add comprehensive tests
4. Update documentation
5. Add usage examples

### Vector Index Implementations

The library uses a protocol-based design. To add support for a new vector database:

1. Implement the `VectorIndex` protocol
2. Create example implementation in `examples/`
3. Document integration steps
4. Add tests if possible

## Reporting Issues

### Bug Reports

Use the GitHub issue template and include:

- Python version
- Library version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages/logs

### Feature Requests

Include:

- Use case description
- Proposed API design
- Benefits/impact
- Potential implementation approach

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Follow the project's coding standards

## Questions?

- Open an issue for questions
- Check existing issues/PRs first
- Review documentation in `docs/`

Thank you for contributing! 🎉


