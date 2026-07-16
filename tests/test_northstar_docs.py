"""Release-contract checks for security, privacy, reliability, and performance docs."""

import re
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


def test_installation_guide_has_no_stale_release_pins() -> None:
    version = tomllib.loads(_read("pyproject.toml"))["project"]["version"]
    guide = _read("docs/installation-guide.md")
    assert set(re.findall(r"(?:@|/download/)v(\d+\.\d+\.\d+)", guide)) == {version}
    assert f"shared-libs-python.git@v{version}" in guide


def test_changelog_links_continue_from_the_current_release() -> None:
    version = tomllib.loads(_read("pyproject.toml"))["project"]["version"]
    changelog = _read("CHANGELOG.md")
    repository = "https://github.com/hseshadr/shared-libs-python"
    assert f"[Unreleased]: {repository}/compare/v{version}...HEAD" in changelog
    assert f"[{version}]: {repository}/compare/v0.1.4...v{version}" in changelog
