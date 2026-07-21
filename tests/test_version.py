"""The package ``__version__`` must never drift from the installed distribution.

Regression guard: ``__version__`` used to be a hardcoded literal in each
``__init__.py`` while the publish workflow's ``sed`` bumped only
``pyproject.toml``. An installed wheel therefore reported a stale version. Both
package versions are now derived from ``importlib.metadata`` so they can only
ever equal the real distribution metadata.
"""

import re
import tomllib
from importlib.metadata import version
from pathlib import Path

import pytest

import edgeproc_core
from edgeproc_core import vector_mgmt

_DISTRIBUTION_VERSION = version("edgeproc-core")

#: What ``__init__.py`` falls back to when the distribution cannot be resolved.
_UNRESOLVED_FALLBACK = "0.0.0+unknown"

_ROOT = Path(__file__).resolve().parents[1]
_INIT_FILES = ("edgeproc_core/__init__.py", "edgeproc_core/vector_mgmt/__init__.py")


def _declared_distribution_name() -> str:
    """The distribution name ``pyproject.toml`` actually publishes under."""
    pyproject = tomllib.loads((_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return str(pyproject["project"]["name"])


def test_top_level_version_matches_distribution_metadata() -> None:
    """``edgeproc_core.__version__`` equals the installed package metadata."""
    assert edgeproc_core.__version__ == _DISTRIBUTION_VERSION


def test_vector_mgmt_version_matches_distribution_metadata() -> None:
    """``vector_mgmt.__version__`` equals the installed package metadata."""
    assert vector_mgmt.__version__ == _DISTRIBUTION_VERSION


@pytest.mark.parametrize("resolved", [edgeproc_core.__version__, vector_mgmt.__version__])
def test_version_is_a_real_version_not_the_unresolved_fallback(resolved: str) -> None:
    """A wrong distribution name degrades ``__version__`` *silently* — catch it loudly.

    ``version("<dist>")`` raises ``PackageNotFoundError`` only for a name nothing
    provides; ``__init__.py`` swallows that into ``0.0.0+unknown``. So a renamed
    distribution whose lookup string was not renamed in lockstep still imports,
    still passes type-checking, and reports a fake version. Nothing else fails.
    """
    assert resolved != _UNRESOLVED_FALLBACK
    assert re.fullmatch(r"\d+\.\d+\.\d+.*", resolved)


@pytest.mark.parametrize("init_file", _INIT_FILES)
def test_metadata_lookup_uses_the_declared_distribution_name(init_file: str) -> None:
    """Each runtime lookup names the distribution ``pyproject.toml`` declares.

    This is the structural guard: renaming the distribution without renaming
    every ``version("...")`` call site fails here, at the source level, instead
    of degrading to the fallback at runtime.
    """
    source = (_ROOT / init_file).read_text(encoding="utf-8")
    looked_up = re.findall(r'version\(\s*"([^"]+)"\s*\)', source)

    assert looked_up, f"{init_file} performs no importlib.metadata version lookup"
    assert set(looked_up) == {_declared_distribution_name()}
