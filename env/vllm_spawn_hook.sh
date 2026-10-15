#!/bin/bash
# Make vLLM start its tensor-parallel workers with "spawn" instead of "fork" in evalenv.
#
# Why: eval.py calls set_seed() (which initialises CUDA) before creating vllm.LLM. With 2 GPUs vLLM 0.6.1 forks
# a worker process, which then dies with "RuntimeError: Cannot re-initialize CUDA in forked subprocess"
# (first seen 2026-10-15 on the first 2-GPU trained-model eval; 1-GPU base evals have no worker, so never hit it).
# eval.py's main code is under `if __name__ == "__main__":`, so spawn is safe. eval/ stays untouched.
#
# How: eval_single.sh does `source activate $CONDA_ENV`, and conda runs every script in the env's
# etc/conda/activate.d/ -- so this also covers eval jobs that are ALREADY queued. Idempotent.
#   bash env/vllm_spawn_hook.sh                 # default: ~/.conda/envs/evalenv
set -euo pipefail
ENV_PREFIX="${1:-$HOME/.conda/envs/evalenv}"
[ -x "$ENV_PREFIX/bin/python" ] || { echo "no env at $ENV_PREFIX"; exit 1; }
mkdir -p "$ENV_PREFIX/etc/conda/activate.d"
echo 'export VLLM_WORKER_MULTIPROC_METHOD=spawn' > "$ENV_PREFIX/etc/conda/activate.d/vllm_spawn.sh"
echo "installed $ENV_PREFIX/etc/conda/activate.d/vllm_spawn.sh"
