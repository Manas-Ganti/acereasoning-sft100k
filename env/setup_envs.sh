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
# Our own analysis scripts need a few packages the requirement files do not list (pandas, pyarrow;
# sentence-transformers, scikit-learn in myenv). They are installed with a constraints file frozen
# from the env first, so they cannot move any tested version.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WHICH="${1:-all}"
module load Miniconda3
module load CUDA/12.6.0

have_env() { conda env list | awk '{print $1}' | grep -qx "$1"; }
add_constrained() {  # pip install extras without changing any already-installed version
    pip freeze | grep -v -E '^(-e|#)| @ ' > /tmp/constraints_$$.txt
    pip install -c /tmp/constraints_$$.txt "$@"
}

if [ "$WHICH" = all ] || [ "$WHICH" = train ]; then
    have_env myenv || conda create -y -n myenv python=3.10
    source activate myenv
    cd "$REPO/LLaMA-Factory"
    pip install -r requirements.txt
    pip install -e ".[torch,metrics]" --no-build-isolation
    pip install flash-attn --no-build-isolation
    pip install deepspeed==0.16.8
    add_constrained pandas pyarrow scikit-learn sentence-transformers wandb
    python -c "import llamafactory, transformers, torch, flash_attn; print('myenv OK: torch', torch.__version__, 'transformers', transformers.__version__)"
    cd "$REPO"
    conda deactivate
fi

if [ "$WHICH" = all ] || [ "$WHICH" = eval ]; then
    have_env evalenv || conda create -y -n evalenv python=3.11
    source activate evalenv
    pip install -r "$REPO/eval/requirements.txt"
    add_constrained pandas pyarrow
    # Guard, not an override: eval/utils/parser.py imports latex2sympy2 at module load, so if this
    # import fails, every eval job dies. Verified locally 2026-10-05 that latex2sympy2 1.9.1 cannot
    # load under antlr4 4.11.1 ("Could not deserialize ATN"); if that happens here, stop and report
    # rather than silently changing a tested pin.
    if ! python -c "from latex2sympy2 import latex2sympy; latex2sympy(r'\frac{1}{2}')" 2>/dev/null; then
        echo "!! latex2sympy2 does not import in evalenv with the tested pins:"
        pip list 2>/dev/null | grep -i -E '^(antlr4-python3-runtime|latex2sympy2) '
        echo "!! The main README's way (pip install --no-deps latex2sympy2==1.9.1, antlr4 4.9.x) is known to work:"
        echo "!!     source activate evalenv && pip install antlr4-python3-runtime==4.9.3"
        exit 1
    fi
    python -c "import vllm, sympy; print('evalenv OK: vllm', vllm.__version__, 'sympy', sympy.__version__)"
fi
echo "Next: bash env/check_envs.sh"
