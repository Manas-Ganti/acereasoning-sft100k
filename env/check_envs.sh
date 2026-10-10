#!/bin/bash
# Login-node preflight, no GPU needed. Run before the first submit and after any env change.
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRAIN_ENV_NAME="${TRAIN_CONDA_ENV:-myenv}"
EVAL_ENV_NAME="${EVAL_CONDA_ENV:-evalenv}"
ACCOUNT="${ACCOUNT:-tml_2026}"
HF_HOME="${HF_HOME:-/home/$USER/hf_cache}"
fail=0
ok()  { echo "  ok   $*"; }
bad() { echo "  FAIL $*"; fail=1; }

module load Miniconda3 >/dev/null 2>&1
TPY="$HOME/.conda/envs/$TRAIN_ENV_NAME/bin/python"   # by path: `conda env list` may query another conda
EPY="$HOME/.conda/envs/$EVAL_ENV_NAME/bin/python"

echo "== interpreters (a 0-byte python prints nothing)"
for p in "$TPY" "$EPY"; do
    v=$("$p" -V 2>&1) && [ -n "$v" ] && ok "$p: $v" || bad "$p is missing or broken"
done

echo "== eval_single.sh's activation from a conda-clean environment (what launch/eval_model.sh hands the job)"
source "$REPO/env/clean_conda.sh"
for e in "$TRAIN_ENV_NAME" "$EVAL_ENV_NAME"; do
    p="$HOME/.conda/envs/$e"
    out=$( (clean_conda_env; bash -c "module load Miniconda3 >/dev/null 2>&1; source activate $p; python -c 'import sys; print(sys.executable)'") 2>&1 | tail -1)
    [[ "$out" == "$p"/* ]] && ok "$e -> $out" || bad "source activate $p gives $out -- see env/clean_conda.sh"
done
echo "   (login-node result only; confirm inside a batch job with launch/test_activation.sh)"

echo "== stray user-site packages (pip installs that missed the env)"
if ls -d ~/.local/lib/python3.13/site-packages/torch >/dev/null 2>&1; then
    echo "       ~/.local/lib/python3.13 holds torch from the failed first setup ($(du -sh ~/.local/lib/python3.13 2>/dev/null | cut -f1)); jobs ignore it (PYTHONNOUSERSITE=1) -- safe to delete"
fi

echo "== $TRAIN_ENV_NAME: training stack (no deepspeed import on a login node: no GPU driver for Triton)"
"$TPY" -c "import llamafactory, transformers, torch, flash_attn, sentence_transformers; print('torch', torch.__version__, 'transformers', transformers.__version__)" \
    && ok "imports" || bad "training imports"
"$TPY" -m pip list 2>/dev/null | grep -i -E '^(deepspeed|flash.attn) ' | sed 's/^/       /'

echo "== $EVAL_ENV_NAME: eval stack + frozen grader"
"$EPY" -c "import vllm, pandas; print('vllm', vllm.__version__)" && ok "imports" || bad "eval imports"
# pandas imports without pyarrow; parquet I/O and `datasets` (fetch_data, build_dev_set, audit) need it.
# pyarrow does not declare numpy as a dependency, so pip can install a release that needs NumPy 2 next to vllm's 1.26.
"$EPY" -c "import numpy, pyarrow, datasets; print('numpy', numpy.__version__, 'pyarrow', pyarrow.__version__, 'datasets', datasets.__version__)" \
    && ok "pyarrow + datasets" || bad "pyarrow/datasets (pyarrow built for another NumPy? pin it to a release that supports numpy 1.26)"
(cd "$REPO/eval" && "$EPY" -c "from utils.grader import check_is_correct; from utils.parser import extract_answer; assert check_is_correct(extract_answer(r'so \boxed{\frac{1}{2}}'), '0.5')") \
    && ok "eval grader: \\boxed{\\frac12} == 0.5" || bad "eval grader (latex2sympy2 / antlr4 -- see env/setup_envs.sh)"
"$EPY" -m pip list 2>/dev/null | grep -i -E '^(antlr4-python3-runtime|latex2sympy2|sympy) ' | sed 's/^/       /'

echo "== HF token under HF_HOME=$HF_HOME (needed for GPQA)"
HF_HOME="$HF_HOME" "$EPY" -c "from huggingface_hub import whoami; print(whoami()['name'])" \
    && ok "token found" || bad "no token: HF_HOME=$HF_HOME huggingface-cli login"

echo "== eval/ unchanged"
bash "$REPO/scripts/check_eval_frozen.sh" && ok "eval/ matches eval.sha256" || bad "eval/ was modified"

echo "== SLURM account $ACCOUNT: partitions / QOS it may use"
assoc=$(sacctmgr -nP show assoc user="$USER" account="$ACCOUNT" format=account,partition,qos 2>/dev/null)
[ -n "$assoc" ] && { ok "associated with $ACCOUNT"; echo "$assoc" | sed 's/^/       /'; } || bad "no association for account $ACCOUNT"
echo "   (launch/common.sh submits with QOS tc_<gpu>_normal_short; set QOS= to override, QOS=none to omit)"

[ $fail = 0 ] && echo "ALL CHECKS PASSED" || { echo "SOME CHECKS FAILED"; exit 1; }
