"""The package ``__version__`` must never drift from the installed distribution.

Regression guard: ``__version__`` used to be a hardcoded literal in each
``__init__.py`` while the publish workflow's ``sed`` bumped only
``pyproject.toml``. An installed wheel therefore reported a stale version. Both
package versions are now derived from ``importlib.metadata`` so they can only
ever equal the real distribution metadata.
"""

from importlib.metadata import version

import shared_libs_python
from shared_libs_python import vector_mgmt

_DISTRIBUTION_VERSION = version("shared-libs-python")


def test_top_level_version_matches_distribution_metadata() -> None:
    """``shared_libs_python.__version__`` equals the installed package metadata."""
    assert shared_libs_python.__version__ == _DISTRIBUTION_VERSION


def test_vector_mgmt_version_matches_distribution_metadata() -> None:
    """``vector_mgmt.__version__`` equals the installed package metadata."""
    assert vector_mgmt.__version__ == _DISTRIBUTION_VERSION
