#!/usr/bin/env bash
# End-to-end demo: walks every shipped example so a stranger can see what the
# library actually does in under a minute. Uses the bundled in-memory factory;
# no external vector DB required.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"

if command -v uv >/dev/null 2>&1 && [ -f "$REPO_ROOT/pyproject.toml" ]; then
    PYTHON=(uv --project "$REPO_ROOT" run python)
else
    PYTHON=(python)
fi

banner() { printf "\n=== %s ===\n" "$1"; }

banner "basic_usage — single global index, tenant_1"
"${PYTHON[@]}" "$HERE/basic_usage.py"

banner "custom_partition_key — bucketed by user_id"
"${PYTHON[@]}" "$HERE/custom_partition_key.py"

banner "composite_partition_key — extractor builds org_id:region"
"${PYTHON[@]}" "$HERE/composite_partition_key.py"

banner "two_tier_partition — hot/cold split by created_at, plus a rebuild"
"${PYTHON[@]}" "$HERE/two_tier_partition.py"

banner "canonical_errors — raw failures become stable codes + RFC 9457"
"${PYTHON[@]}" "$HERE/canonical_errors.py"

printf "\nAll examples ran successfully.\n"
