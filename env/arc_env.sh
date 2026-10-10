# Sourced by every slurm/*.slurm job body:   [REQUIRE_ENV=<myenv|evalenv>] source "$REPO/env/arc_env.sh"
#
# Env selection: $SFT_ENV = myenv (training/embeddings) or evalenv (eval/scoring), always set explicitly by
# launch/*.sh. NOT $CONDA_ENV: the login ~/.bashrc exports CONDA_ENV=.../miniconda3/envs/vrr (another project),
# which leaked into the first audit job.
# We do NOT use `source activate`: on ARC's Miniconda3 25.11 module it can return success without
# switching interpreters in a batch shell. Instead PY / CONDA_PREFIX / PATH are set directly from the
# env's absolute path, and every job body calls "$PY", never a bare `python`. Also (arc_runbook.md):
#  * `conda env list` on a login node may query a different conda -> resolve envs by path instead;
#  * assert the interpreter is a real binary (`python -V` must print; a 0-byte python once made
#    every job "succeed" in 2 s);
#  * sentinel import for the env the job needs (REQUIRE_ENV), so a wrong-env job dies in seconds,
#    not after an 8-GPU allocation;
#  * explicit HF_HOME (the HF token lives under it);
#  * NCCL_SOCKET_IFNAME probed per node (`ib0` exists on H200 nodes but has no IPv4 address).
: "${REPO:?REPO must be exported by the launcher (launch/*.sh does this)}"
cd "$REPO"
unset PYTHONPATH                               # nothing inherited from other projects
export HF_HOME="${HF_HOME:-/home/$USER/hf_cache}"
export WANDB_DIR="${WANDB_DIR:-/home/$USER/wandb}"
export WANDB_PROJECT="${WANDB_PROJECT:-acereason-sft-selection}"
export PYTHONUNBUFFERED=1
mkdir -p "$WANDB_DIR" "$REPO/logs/slurm"
SECRETS_FILE="${SECRETS_FILE:-$HOME/.config/vrr/secrets.env}"   # WANDB_API_KEY etc., outside the repo
[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE"
# report_to: wandb is in the README YAML. Without a W&B login, wandb.init crashes a batch job (no tty),
# so log offline instead (runs land in $WANDB_DIR; `wandb sync` uploads them later). Training is unaffected.
if [ -z "${WANDB_MODE:-}" ] && [ -z "${WANDB_API_KEY:-}" ] && ! grep -qs api.wandb.ai ~/.netrc; then
    export WANDB_MODE=offline
fi

if command -v module &>/dev/null; then
    module load Miniconda3
    module load CUDA/12.6.0
fi
export PYTHONNOUSERSITE=1                       # keep ~/.local site-packages out of every job
case "${SFT_ENV:-}" in
    myenv|evalenv) ;;
    *) echo "[arc_env] FATAL: SFT_ENV must be myenv or evalenv (got '${SFT_ENV:-}'); launch/*.sh sets it" >&2; exit 3 ;;
esac
ENV_PREFIX="$HOME/.conda/envs/$SFT_ENV"
[ -x "$ENV_PREFIX/bin/python" ] || { echo "[arc_env] FATAL: no env at $ENV_PREFIX" >&2; exit 3; }
export CONDA_PREFIX="$ENV_PREFIX" CONDA_DEFAULT_ENV="$(basename "$ENV_PREFIX")"
export PATH="$ENV_PREFIX/bin:$PATH"
export PY="$ENV_PREFIX/bin/python"
if ! "$PY" -V 2>&1 | grep -q '^Python 3'; then
    echo "[arc_env] FATAL: $PY did not print a version -- broken or 0-byte interpreter" >&2; exit 3
fi
exe=$("$PY" -c 'import sys; print(sys.executable)')
[[ "$exe" == "$ENV_PREFIX"/* ]] || { echo "[arc_env] FATAL: sys.executable=$exe is not inside $ENV_PREFIX" >&2; exit 3; }
if [ -n "${REQUIRE_ENV:-}" ] && [ "$REQUIRE_ENV" != "$SFT_ENV" ]; then
    echo "[arc_env] FATAL: this job needs env $REQUIRE_ENV, launcher gave SFT_ENV=$SFT_ENV" >&2; exit 3
fi
case "$SFT_ENV" in   # sentinel import: the env really is what it claims to be
    myenv)   sentinel="import llamafactory, transformers, flash_attn" ;;
    evalenv) sentinel="import vllm; from latex2sympy2 import latex2sympy" ;;
esac
"$PY" -c "$sentinel" 2>/dev/null || { echo "[arc_env] FATAL: sentinel import failed in $SFT_ENV: $sentinel" >&2; exit 3; }

if [ -z "${NCCL_SOCKET_IFNAME:-}" ] && command -v ip &>/dev/null; then
    for cand in ib0 eth0 $(ls /sys/class/net 2>/dev/null); do
        case "$cand" in lo|docker*|veth*|virbr*) continue ;; esac
        if ip -o -4 addr show dev "$cand" 2>/dev/null | grep -q inet; then
            export NCCL_SOCKET_IFNAME="$cand"; break
        fi
    done
fi
echo "[arc_env] host=$(hostname) job=${SLURM_JOB_ID:-none} env=$SFT_ENV python=$PY"
echo "[arc_env] HF_HOME=$HF_HOME WANDB_MODE=${WANDB_MODE:-online} NCCL_SOCKET_IFNAME=${NCCL_SOCKET_IFNAME:-unset} CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
