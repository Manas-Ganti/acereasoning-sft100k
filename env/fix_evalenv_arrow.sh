#!/bin/bash
# Make pyarrow (and therefore pandas parquet I/O and `datasets`, which eval/ imports) work in evalenv
# without moving its tested stack.
#
# Why: eval/requirements.txt leaves `datasets` unpinned. On a fresh build it pulls the newest pyarrow,
# and pyarrow does not declare numpy as a dependency, so pip happily installs a release built for
# NumPy 2 next to vllm 0.6.1's numpy 1.26 ("pyarrow requires NumPy 2.0 or newer, found 1.26.4").
# Seen on a 2026-10-10 build: datasets 5.0.1, pandas 3.0.6, pyarrow 26.0.0, numpy 1.26.4.
#
# What: keep numpy / torch / transformers / tokenizers / vllm frozen, walk pyarrow down one major
# release at a time until `import pyarrow, datasets` works and a pandas parquet round trip passes;
# pip may move `datasets` (and pandas, last resort) to versions that accept that pyarrow.
#   bash env/fix_evalenv_arrow.sh            # idempotent: exits at once if the env already works
set -uo pipefail
export PYTHONNOUSERSITE=1
PY="${PY:-$HOME/.conda/envs/evalenv/bin/python}"
[ -x "$PY" ] || { echo "no python at $PY"; exit 1; }

probe() {
    "$PY" - <<'EOF' 2>/dev/null
import io
import numpy, pyarrow, pandas, datasets
df = pandas.DataFrame({"a": [1, 2], "s": ["x", "y"]})
buf = io.BytesIO(); df.to_parquet(buf, compression="zstd"); buf.seek(0)
assert pandas.read_parquet(buf).equals(df)
print(f"ok  numpy {numpy.__version__}  pyarrow {pyarrow.__version__}  pandas {pandas.__version__}  datasets {datasets.__version__}")
EOF
}

if probe; then echo "evalenv parquet/datasets already work -- nothing to do"; exit 0; fi

PINS=$(mktemp)
"$PY" -m pip freeze | grep -i -E '^(numpy|torch|transformers|tokenizers|vllm)==' > "$PINS"
echo "frozen during the fix:"; sed 's/^/  /' "$PINS"
grep -q '^numpy==1\.' "$PINS" || { echo "numpy is not 1.x -- this script assumes vllm 0.6.1's numpy 1.26"; exit 1; }

try() {  # try <pip args...>: install under the frozen pins, then probe
    "$PY" -m pip install -q -c "$PINS" "$@" datasets >/dev/null 2>&1 && probe
}

cur=$("$PY" -m pip list 2>/dev/null | awk 'tolower($1)=="pyarrow"{split($2,v,"."); print v[1]}')
for major in $(seq $(( ${cur:-26} - 1 )) -1 15); do
    echo "-- trying pyarrow $major.*"
    try "pyarrow==$major.*" && { rm -f "$PINS"; echo "FIXED (record these versions in docs/STATUS.md)"; exit 0; }
    echo "-- trying pyarrow $major.* with pandas<3"
    try "pyarrow==$major.*" "pandas<3" && { rm -f "$PINS"; echo "FIXED (record these versions in docs/STATUS.md)"; exit 0; }
done
rm -f "$PINS"
echo "no pyarrow release 15..$cur works with this env -- paste the output of: $PY -c 'import pyarrow'"
exit 1
