#!/bin/bash
# Environment setup on an ARC login node, from the repo root. Uses the course repo's TESTED
# requirement files as-is; nothing here re-pins a version they specify.
#     bash env/setup_envs.sh            # both envs
#     bash env/setup_envs.sh train      # myenv only
#     bash env/setup_envs.sh eval       # evalenv only
#
#   myenv    (python 3.10)  README section 1.1/1.3/1.4: LLaMA-Factory/requirements.txt,
#                            pip install -e ".[torch,metrics]", flash-attn, deepspeed==0.16.8
#                            -> training, prompt embeddings/clustering, HF upload
#   evalenv  (python 3.11)  eval/README section 2: pip install -r eval/requirements.txt
#                            -> eval_single.sh (CONDA_ENV=evalenv), dev eval, pool audit/scoring/grading,
#                               selection, results
#
# Lessons from the first run on ARC (2026-10-05):
#  * `source activate <env>` inside this script did NOT switch interpreters (Miniconda3 25.11 module):
#    pip ran from the base Python 3.13 and installed into ~/.local. So every pip call below goes
#    through the env's own interpreter by absolute path, and PYTHONNOUSERSITE=1 keeps ~/.local out.
#  * The README's unpinned `torch` (via LLaMA-Factory's `.[torch]` extra) now resolves to torch 2.14
#    built for CUDA 13.0: no prebuilt flash-attn wheel exists for it, and a source build fails against
#    the cluster's CUDA 12.6 module. torch is therefore pinned to 2.6.0+cu126 (matches CUDA/12.6.0;
#    prebuilt flash-attn wheels exist; proven on these nodes). No requirement file pins torch, so
#    this does not override a tested pin.
#
# Our own analysis scripts need a few packages the requirement files do not list (pandas, pyarrow;
# sentence-transformers, scikit-learn, wandb in myenv). They are installed with a constraints file
# frozen from the env first, so they cannot move any tested version.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHICH="${1:-all}"
export PYTHONNOUSERSITE=1
module load Miniconda3
module load CUDA/12.6.0

TORCH_PIN=(torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu126)

env_prefix() { conda env list | awk -v e="$1" '$1==e {print $NF}'; }
make_env() {  # make_env <name> <python version> -> prints prefix
    local name=$1 ver=$2 prefix
    prefix=$(env_prefix "$name")
    if [ -z "$prefix" ]; then
        conda create -y -q -n "$name" "python=$ver" >&2
        prefix=$(env_prefix "$name")
    fi
    [ -x "$prefix/bin/python" ] || { echo "env $name has no python at $prefix" >&2; exit 1; }
    local have; have=$("$prefix/bin/python" -c 'import sys; print("%d.%d" % sys.version_info[:2])')
    [ "$have" = "$ver" ] || { echo "env $name exists with python $have, expected $ver -- remove it: conda env remove -n $name" >&2; exit 1; }
    echo "$prefix"
}
add_constrained() {  # add_constrained <python> <pkgs...>: install extras without moving any installed version
    local py=$1; shift
    "$py" -m pip freeze | grep -v -E '^(-e|#)| @ ' > /tmp/constraints_$$.txt
    "$py" -m pip install -c /tmp/constraints_$$.txt "$@"
}

if [ "$WHICH" = all ] || [ "$WHICH" = train ]; then
    P=$(make_env myenv 3.10); PY="$P/bin/python"
    echo "== myenv: $PY"
    cd "$REPO/LLaMA-Factory"
    "$PY" -m pip install "${TORCH_PIN[@]}"
    "$PY" -m pip install -r requirements.txt
    "$PY" -m pip install -e ".[torch,metrics]" --no-build-isolation
    # flash-attn's setup.py downloads its prebuilt wheel and os.rename()s it into pip's cache in
    # /home; with TMPDIR on /tmp (another filesystem on ARC) that fails with "Invalid cross-device
    # link". Keep the build temp dir on the same filesystem as the cache.
    mkdir -p "$HOME/.cache/pip-tmp"
    TMPDIR="$HOME/.cache/pip-tmp" "$PY" -m pip install flash-attn --no-build-isolation
    rm -rf "$HOME/.cache/pip-tmp"
    "$PY" -m pip install deepspeed==0.16.8
    add_constrained "$PY" pandas pyarrow scikit-learn sentence-transformers wandb
    "$PY" -c "import torch; assert torch.__version__.startswith('2.6.0'), 'torch was moved to ' + torch.__version__"
    "$PY" -c "import llamafactory, transformers, torch, flash_attn; print('myenv OK: torch', torch.__version__, 'transformers', transformers.__version__, 'flash_attn', flash_attn.__version__)"
    cd "$REPO"
fi

if [ "$WHICH" = all ] || [ "$WHICH" = eval ]; then
    P=$(make_env evalenv 3.11); PY="$P/bin/python"
    echo "== evalenv: $PY"
    # eval/requirements.txt, installed in stages (2026-10-05, on ARC):
    #  * its unpinned `transformers` now resolves to 5.x, which vllm<=0.6.1 (Sep 2024) predates; pin the
    #    release contemporary with vLLM 0.6.1 (the file does not pin transformers);
    #  * `flash_attn` cannot be built inside `pip install -r` (its setup imports torch, which the isolated
    #    build env lacks). vLLM 0.6.1 bundles its own attention kernels and eval/ never imports
    #    flash_attn, so it is installed afterwards the README way and is not fatal if no wheel exists.
    "$PY" -m pip install "vllm<=0.6.1" "transformers==4.44.2"
    #  * the file's own pins antlr4-python3-runtime==4.11.1 and latex2sympy2==1.9.1 cannot coexist
    #    (latex2sympy2 requires antlr4==4.7.2: ResolutionImpossible, confirmed on ARC 2026-10-05; under
    #    4.11.1 latex2sympy2 cannot even be imported). Decided 2026-10-05: follow the main README --
    #    `pip install --no-deps latex2sympy2==1.9.1` with antlr4 at 4.9.x (omegaconf's pin) -> 4.9.3.
    grep -v -E '^\s*(flash_attn|antlr4-python3-runtime|latex2sympy2)' "$REPO/eval/requirements.txt" > /tmp/evalreq_$$.txt
    "$PY" -m pip freeze | grep -i -E '^(torch|transformers|tokenizers|vllm)==' > /tmp/evalpin_$$.txt
    "$PY" -m pip install -r /tmp/evalreq_$$.txt -c /tmp/evalpin_$$.txt
    "$PY" -m pip install "antlr4-python3-runtime==4.9.3"
    "$PY" -m pip install --no-deps latex2sympy2==1.9.1
    mkdir -p "$HOME/.cache/pip-tmp"
    TMPDIR="$HOME/.cache/pip-tmp" "$PY" -m pip install flash_attn --no-build-isolation -c /tmp/evalpin_$$.txt \
        || echo "!! flash_attn not installed in evalenv (no prebuilt wheel); eval does not use it -- continuing"
    rm -rf "$HOME/.cache/pip-tmp"
    add_constrained "$PY" pandas pyarrow
    "$PY" -c "import transformers; assert transformers.__version__ == '4.44.2', 'transformers moved to ' + transformers.__version__"
    # eval/utils/parser.py imports latex2sympy2 at module load: if this fails, every eval job dies.
    "$PY" -c "from latex2sympy2 import latex2sympy; print('latex2sympy2 OK:', latex2sympy(r'\frac{1}{2}'))" \
        || { echo "!! latex2sympy2 does not import in evalenv"; exit 1; }
    "$PY" -c "import vllm, sympy, torch; print('evalenv OK: vllm', vllm.__version__, 'torch', torch.__version__, 'sympy', sympy.__version__)"
fi

echo "== does 'source activate' work in a batch-style shell? (eval_single.sh relies on it)"
for e in myenv evalenv; do
    p=$(env_prefix "$e"); [ -n "$p" ] || continue
    got=$(bash -c "module load Miniconda3 >/dev/null 2>&1; source activate $e >/dev/null 2>&1; command -v python")
    [ "$got" = "$p/bin/python" ] && echo "   $e: ok" || echo "   $e: NO -- resolves to $got (launchers pin PATH to work around this)"
done
echo "Next: bash env/check_envs.sh"
