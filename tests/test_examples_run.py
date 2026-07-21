"""Every shipped example must actually run, and `run_loop.sh` must list them all.

An example is the only place a reader sees a capability working. If one rots,
the documentation is silently wrong; if one exists but is missing from
`run_loop.sh`, the "run all the examples" path quietly skips it.

These tests execute each example in a subprocess — the same way a reader runs
it — rather than importing it, so an import-time-only success cannot pass for a
working script.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def _example_scripts() -> list[Path]:
    """Every runnable example script (excluding the package marker)."""
    return sorted(path for path in EXAMPLES.glob("*.py") if path.name != "__init__.py")


def test_there_are_examples_to_check() -> None:
    """Non-vacuity: the parametrized runs below must not be an empty set."""
    assert len(_example_scripts()) >= 5


@pytest.mark.parametrize("script", _example_scripts(), ids=lambda path: path.stem)
def test_example_runs_cleanly(script: Path) -> None:
    """The example exits 0 and prints something a reader can look at."""
    result = subprocess.run(  # noqa: S603
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=120,
        check=False,  # the assertion below reports the failure with its stderr
    )

    assert result.returncode == 0, f"{script.name} failed:\n{result.stderr}"
    assert result.stdout.strip(), f"{script.name} produced no output"


@pytest.mark.parametrize("script", _example_scripts(), ids=lambda path: path.stem)
def test_example_is_wired_into_the_run_loop(script: Path) -> None:
    """A shipped example that `run_loop.sh` never calls is invisible to readers."""
    assert script.name in (EXAMPLES / "run_loop.sh").read_text(encoding="utf-8")
