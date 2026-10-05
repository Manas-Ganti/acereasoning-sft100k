#!/bin/bash
#SBATCH --job-name=deveval
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
# Dev-set eval with the UNMODIFIED eval/eval.py: run from dev/ so ./prompts and --data_dir point at
# the dev data (eval.py imports its utils from its own directory). Same sampling settings as the
# test eval except n_sampling (DEV_N, default 4) to save GPU time.
#   sbatch ... slurm/dev_eval.slurm <model path or HF id> <run name>
set -eo pipefail
MODEL="$1"; RUN="$2"
REQUIRE_ENV=evalenv source "$REPO/env/arc_env.sh"
bash "$REPO/scripts/check_eval_frozen.sh"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
OUT="$REPO/work/dev_eval/$RUN"
mkdir -p "$OUT"
cd "$REPO/dev"
for SET in $(ls data); do
    "$PY" "$REPO/eval/eval.py" --model_name_or_path "$MODEL" --data_dir ./data --data_name "$SET" \
        --prompt_type qwen-instruct --temperature 0.6 --top_p 0.95 --start_idx 0 --end_idx -1 \
        --n_sampling "${DEV_N:-4}" --k 1 --split test --max_tokens 32768 --seed 0 --surround_with_messages \
        --output_dir "$OUT" --completions_save_dir "$OUT/completions" --gpu_memory_utilization 0.92 \
        2>&1 | tee "$OUT/log_$SET.txt"
done
