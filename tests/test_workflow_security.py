"""GitHub Actions must resolve third-party code from immutable commits.

A moving tag (`@v4`) is a supply-chain hole: whoever controls the tag controls
what runs in CI. Only a full 40-character commit SHA is immutable.

This check globs **both** YAML extensions. It previously matched `*.yml` alone,
so a `deploy.yaml` carrying an unpinned action would have passed without ever
being opened — a green result that proved nothing. The reference count is
asserted non-zero for the same reason: a test that inspects nothing must fail
rather than quietly succeed.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)", re.MULTILINE)
PINNED = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40}$")
YAML_GLOBS = ("*.yml", "*.yaml")


def _workflow_files(directory: Path) -> list[Path]:
    """Every workflow file in ``directory``, under either YAML extension."""
    return sorted(path for glob in YAML_GLOBS for path in directory.glob(glob))


def _unpinned(action: str) -> bool:
    """Whether ``action`` resolves to something other than a full commit SHA."""
    return not action.startswith("./") and PINNED.fullmatch(action) is None


def _audit(directory: Path) -> tuple[list[str], int]:
    """Return ``(failures, references_examined)`` for the workflows in ``directory``."""
    failures: list[str] = []
    examined = 0
    for workflow in _workflow_files(directory):
        for action in USES.findall(workflow.read_text(encoding="utf-8")):
            examined += 1
            if _unpinned(action):
                failures.append(f"{workflow.name}: {action}")
    return failures, examined


def test_external_actions_are_pinned_to_full_commit_shas() -> None:
    """No workflow may reference a third-party action by a moving tag."""
    failures, examined = _audit(WORKFLOWS)

    assert failures == []
    assert examined > 0, "vacuous pass: no `uses:` reference was examined"


def test_the_audit_reports_nothing_examined_for_an_empty_directory(tmp_path: Path) -> None:
    """Non-vacuity proof: with no workflows to read, the count is zero.

    This is what makes the `examined > 0` assertion above meaningful — it shows
    the counter reflects work actually done, so an empty or mis-globbed
    directory cannot masquerade as a clean audit.
    """
    assert _audit(tmp_path) == ([], 0)


@pytest.mark.parametrize("extension", [".yml", ".yaml"])
def test_an_unpinned_action_is_caught_under_either_extension(
    tmp_path: Path, extension: str
) -> None:
    """The original defect: a `.yaml` workflow was never opened."""
    workflow = tmp_path / f"deploy{extension}"
    workflow.write_text("jobs:\n  a:\n    steps:\n      - uses: foo/bar@v4\n")

    failures, examined = _audit(tmp_path)

    assert failures == [f"deploy{extension}: foo/bar@v4"]
    assert examined == 1


def test_a_full_sha_and_a_local_action_both_pass(tmp_path: Path) -> None:
    """Guard the opposite direction: valid references must not be flagged."""
    sha = "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"
    body = f"steps:\n  - uses: a/b@{sha}\n  - uses: ./.github/actions/x\n"
    (tmp_path / "ok.yaml").write_text(body)

    assert _audit(tmp_path) == ([], 2)
