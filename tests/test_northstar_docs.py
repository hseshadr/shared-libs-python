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
    assert f"/download/v{version}/edgeproc_core-{version}-" in readme


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


def test_the_gate_measures_branch_coverage_not_just_statements() -> None:
    """The README publishes a *branch* figure, so the gate must measure branches.

    `--cov-branch` was once absent, which made the published "98.62% branch
    coverage" really statement coverage. This pins the stricter measurement in
    place so the claim and the gate cannot drift apart again.
    """
    pytest_config = tomllib.loads(_read("pyproject.toml"))["tool"]["pytest"]["ini_options"]

    assert "--cov-branch" in pytest_config["addopts"]


def test_published_coverage_floor_matches_the_configured_floor() -> None:
    """The floor the docs promise is the floor the gate actually enforces."""
    config = tomllib.loads(_read("pyproject.toml"))
    configured = config["tool"]["coverage"]["report"]["fail_under"]
    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]

    assert f"--cov-fail-under={configured:.0f}" in addopts
    assert f"≥{configured:.0f}% branch coverage" in _read("README.md")
