"""Release-contract checks for security, privacy, reliability, and performance docs."""

import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_security_policy_supports_the_current_release_line() -> None:
    assert "| 0.2.x" in _read("SECURITY.md")


@pytest.mark.parametrize(
    "heading",
    [
        "## Threat model and trust boundaries",
        "## Privacy and data flow",
        "## Reliability and recovery contract",
        "## Measured performance contract",
    ],
)
def test_operations_contract_exposes_distinguished_engineer_gates(heading: str) -> None:
    assert heading in _read("docs/OPERATIONS.md")


def test_readme_links_the_operations_contract() -> None:
    assert "docs/OPERATIONS.md" in _read("README.md")


def test_readme_status_and_install_examples_match_package_version() -> None:
    project = tomllib.loads(_read("pyproject.toml"))["project"]
    version = project["version"]
    readme = _read("README.md")
    assert f"**Status:** v{version}" in readme
    assert f"shared-libs-python.git@v{version}" in readme
    assert f"/download/v{version}/shared_libs_python-{version}-" in readme
