#!/bin/bash
# Verifies eval/ is byte-identical to the upstream copy recorded in eval.sha256.
# Invariant: never modify eval/. Generated outputs (eval/outputs, eval/completions) are ignored.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 1
if command -v sha256sum &>/dev/null; then SHA="sha256sum"; else SHA="shasum -a 256"; fi
$SHA -c --quiet eval.sha256 || { echo "eval/ differs from eval.sha256 -- restore it (git checkout eval/)"; exit 1; }
extra=$(find eval -type f -not -name '.DS_Store' -not -path 'eval/outputs/*' -not -path 'eval/completions/*' \
        -not -path '*/__pycache__/*' | LC_ALL=C sort | comm -23 - <(awk '{print $2}' eval.sha256 | LC_ALL=C sort))
[ -z "$extra" ] || { echo "unexpected files in eval/:"; echo "$extra"; exit 1; }
