# Sourced by every slurm/*.slurm job body:   source "$REPO/env/arc_env.sh"
#
# Activation follows the upstream README (module load Miniconda3 + CUDA/12.6.0, source activate
# $CONDA_ENV: myenv for training/embeddings, evalenv for eval/scoring -- set by launch/*.sh),
# plus checks learned the hard way on ARC (arc_runbook.md):
#  * assert the activated python really lives in the env (`source activate` can silently no-op
#    in a batch shell) and is a real binary (`python -V` must print; a 0-byte python once made
#    every job "succeed" in 2 s);
#  * explicit HF_HOME (the HF token lives under it);
#  * NCCL_SOCKET_IFNAME probed per node (`ib0` exists on H200 nodes but has no IPv4 address).
: "${REPO:?REPO must be exported by the launcher (launch/*.sh does this)}"
cd "$REPO"
export CONDA_ENV="${CONDA_ENV:-myenv}"
export HF_HOME="${HF_HOME:-/home/$USER/hf_cache}"
export WANDB_DIR="${WANDB_DIR:-/home/$USER/wandb}"
export WANDB_PROJECT="${WANDB_PROJECT:-acereason-sft-selection}"
export PYTHONUNBUFFERED=1
mkdir -p "$WANDB_DIR" "$REPO/logs/slurm"
SECRETS_FILE="${SECRETS_FILE:-$HOME/.config/vrr/secrets.env}"   # WANDB_API_KEY etc., outside the repo
[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE"

if command -v module &>/dev/null; then
    module load Miniconda3
    module load CUDA/12.6.0
fi
export PYTHONNOUSERSITE=1                       # keep ~/.local site-packages out of every job
source activate "$CONDA_ENV" || true
ENV_PREFIX=$(conda env list | awk -v e="$CONDA_ENV" '$1==e {print $NF}')
[ -n "$ENV_PREFIX" ] || ENV_PREFIX="$CONDA_ENV"   # CONDA_ENV may be an absolute path
export PY="$ENV_PREFIX/bin/python"
# `source activate` silently did not switch interpreters on ARC (Miniconda3 25.11); fall back to PATH.
[ "$(command -v python)" = "$PY" ] || export PATH="$ENV_PREFIX/bin:$PATH"
if ! "$PY" -V 2>&1 | grep -q '^Python 3'; then
    echo "[arc_env] FATAL: $PY did not print a version -- broken or 0-byte interpreter" >&2; exit 3
fi
if [ "$(command -v python)" != "$PY" ]; then
    echo "[arc_env] FATAL: 'python' resolves to $(command -v python), not $PY (activation failed)" >&2; exit 3
fi

if [ -z "${NCCL_SOCKET_IFNAME:-}" ] && command -v ip &>/dev/null; then
    for cand in ib0 eth0 $(ls /sys/class/net 2>/dev/null); do
        case "$cand" in lo|docker*|veth*|virbr*) continue ;; esac
        if ip -o -4 addr show dev "$cand" 2>/dev/null | grep -q inet; then
            export NCCL_SOCKET_IFNAME="$cand"; break
        fi
    done
fi
echo "[arc_env] host=$(hostname) job=${SLURM_JOB_ID:-none} python=$PY"
echo "[arc_env] HF_HOME=$HF_HOME NCCL_SOCKET_IFNAME=${NCCL_SOCKET_IFNAME:-unset} CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-unset}"
