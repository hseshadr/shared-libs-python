"""Release-contract checks for the docs: install paths, provenance, and claims.

The most important check here is
`test_documented_install_refs_actually_ship_the_import_package`. An earlier
version of this file asserted that the README contained a specific install
*string*. That is a spelling check, not a contract: the string it pinned
(`shared-libs-python.git@v0.2.0`) installed the pre-rename `shared_libs_python`
package, so every documented `import edgeproc_core` example raised
`ModuleNotFoundError` — and the guard certified the break instead of catching
it. The check now resolves each documented ref against Git and asserts the tree
at that ref really contains the import package the docs tell you to import.
"""

import re
import subprocess
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
IMPORT_PACKAGE = "edgeproc_core"
REPO_SLUG = "shared-libs-python"

#: Docs that carry user-facing install commands.
INSTALL_DOCS = ("README.md", "docs/installation-guide.md")

#: A ref is "pinned" if it cannot move under an installer: a full commit SHA or
#: a version tag. Moving refs (`main`) are development-only and excluded here;
#: `test_moving_ref_is_labelled_development_only` covers those instead.
_PINNED_REF = re.compile(r"^(?:[0-9a-f]{40}|v\d+\.\d+\.\d+)$")


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _documented_install_refs() -> set[str]:
    """Every ref the docs tell a user to install from."""
    pattern = re.compile(rf"{re.escape(REPO_SLUG)}\.git@([0-9a-zA-Z._-]+)")
    return {ref for doc in INSTALL_DOCS for ref in pattern.findall(_read(doc))}


def _pinned_install_refs() -> set[str]:
    return {ref for ref in _documented_install_refs() if _PINNED_REF.match(ref)}


@pytest.fixture(scope="module")
def git_repo_available() -> bool:
    """Skip Git-backed checks where there is no repository (e.g. an unpacked sdist)."""
    if not (ROOT / ".git").exists() or _git("rev-parse", "--git-dir").returncode != 0:
        pytest.skip("not a git checkout; cannot resolve documented refs")
    return True


def test_docs_document_at_least_one_install_ref() -> None:
    """Guard the guard: if the regex stops matching, the checks below go vacuous."""
    assert _pinned_install_refs(), (
        f"No pinned install ref found in {INSTALL_DOCS}. Either the docs lost their "
        f"install command or the extraction pattern needs updating."
    )


def test_documented_install_refs_actually_ship_the_import_package(
    git_repo_available: bool,
) -> None:
    """Installing any documented ref must yield a working `import edgeproc_core`.

    This is the check that would have caught the `v0.2.0` breakage: that tag
    resolves fine and installs fine, but its tree holds `shared_libs_python`,
    so the README's own examples fail at import time.
    """
    for ref in sorted(_pinned_install_refs()):
        resolved = _git("rev-parse", "--verify", f"{ref}^{{commit}}")
        assert resolved.returncode == 0, (
            f"Documented install ref {ref!r} does not resolve to a commit in this "
            f"repository. A documented ref must exist before it is published."
        )

        listing = _git("ls-tree", "--name-only", ref, f"{IMPORT_PACKAGE}/")
        assert listing.stdout.strip(), (
            f"Documented install ref {ref!r} does not contain the {IMPORT_PACKAGE}/ "
            f"package, so `pip install ...@{ref}` followed by "
            f"`import {IMPORT_PACKAGE}` raises ModuleNotFoundError. "
            f"Point the docs at a ref whose tree actually ships {IMPORT_PACKAGE}/."
        )


def test_moving_ref_is_labelled_development_only() -> None:
    """`@main` may appear, but never as the recommended path for applications."""
    guide = _read("docs/installation-guide.md")
    if f"{REPO_SLUG}.git@main" not in guide:
        return
    assert "development-only" in guide or "Development installs" in guide, (
        "The docs install from the moving `main` ref without marking that path "
        "development-only. Applications must be told to pin."
    )


def test_readme_and_guide_agree_on_the_pinned_ref() -> None:
    """One pin, documented once, in both places — so they cannot drift apart."""
    readme_refs = {
        ref
        for ref in re.findall(rf"{re.escape(REPO_SLUG)}\.git@([0-9a-f]{{40}})", _read("README.md"))
    }
    guide_refs = {
        ref
        for ref in re.findall(
            rf"{re.escape(REPO_SLUG)}\.git@([0-9a-f]{{40}})",
            _read("docs/installation-guide.md"),
        )
    }
    assert readme_refs == guide_refs, (
        f"README pins {readme_refs or '{}'} but the installation guide pins "
        f"{guide_refs or '{}'}. A reader following either must get the same code."
    )


def test_docs_do_not_advertise_a_release_artifact_that_does_not_exist() -> None:
    """No doc may link a GitHub Release wheel until a release actually publishes one.

    The README once linked `edgeproc_core-0.2.0-py3-none-any.whl`, which 404s:
    the `v0.2.0` release predates the rename and its asset is named
    `shared_libs_python-0.2.0-py3-none-any.whl`.
    """
    for doc in INSTALL_DOCS:
        assert "/releases/download/" not in _read(doc), (
            f"{doc} links a GitHub Release download URL. Release assets are only "
            f"linkable once the corresponding release exists and carries that "
            f"exact filename; verify with curl before documenting one."
        )


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
def test_operations_contract_documents_its_required_sections(heading: str) -> None:
    assert heading in _read("docs/OPERATIONS.md")


def test_readme_links_the_operations_contract() -> None:
    assert "docs/OPERATIONS.md" in _read("README.md")


def test_readme_status_matches_package_version() -> None:
    version = tomllib.loads(_read("pyproject.toml"))["project"]["version"]
    assert f"**Status:** v{version}" in _read("README.md")


def test_readme_states_the_python_requirement_before_installing() -> None:
    """A cold reader on 3.12 must learn why the install fails before they run it."""
    readme = _read("README.md")
    requires = tomllib.loads(_read("pyproject.toml"))["project"]["requires-python"]
    minimum = requires.lstrip(">=~^ ")

    assert f"Python {minimum}" in readme, (
        f"README never states the Python {minimum} requirement; `pip install` on an "
        f"older interpreter fails with an unhelpful resolver error."
    )
    assert readme.index(f"Python {minimum}") < readme.index("uv pip install"), (
        "The Python requirement must appear before the first install command."
    )


def test_changelog_links_continue_from_the_current_release() -> None:
    version = tomllib.loads(_read("pyproject.toml"))["project"]["version"]
    changelog = _read("CHANGELOG.md")
    repository = f"https://github.com/hseshadr/{REPO_SLUG}"
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
