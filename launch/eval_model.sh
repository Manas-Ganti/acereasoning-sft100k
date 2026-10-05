#!/bin/bash
# README sections 2 and 6 -- evaluate one model on all 8 benchmarks, the README way:
#     cd eval; MODEL=... OUTPUT_DIR=... sbatch eval_single.sh <benchmark>
# one job per benchmark, in parallel. eval_single.sh is submitted UNMODIFIED; only scheduling
# flags (account / partition / QOS / GPU type / wall time) are given on the sbatch command line,
# which take precedence over its #SBATCH lines (the README says to edit those, but eval/ is frozen).
#
#   launch/eval_model.sh base                         # Qwen/Qwen2.5-3B-Instruct
#   launch/eval_model.sh random_s1                    # LLaMA-Factory/saves/qwen25_3b_instruct/random_s1
#   AFTER=<train jobid> launch/eval_model.sh random_s1
#   BENCHES="aime amc" launch/eval_model.sh random_s1
# Outputs: eval/outputs/<run>/log_<bench>.txt and <model>/<bench>/*.jsonl (a fresh OUTPUT_DIR per
# model, since an existing jsonl makes eval skip that benchmark).
source "$(dirname "$0")/common.sh"
RUN="${1:?run name: base, or a saves/qwen25_3b_instruct/<run>}"
if [ "$RUN" = base ]; then MODEL="Qwen/Qwen2.5-3B-Instruct"; else MODEL="$REPO/LLaMA-Factory/saves/qwen25_3b_instruct/$RUN"; fi
bash "$REPO/scripts/check_eval_frozen.sh" || exit 1
if [ "$RUN" != base ] && [ -z "${AFTER:-}" ] && [ ! -f "$MODEL/DONE" ]; then
    echo "$MODEL has no DONE marker (training not finished?)"; exit 1
fi

# eval_single.sh reads these from the environment (sbatch exports the environment by default).
export MODEL OUTPUT_DIR="$REPO/eval/outputs/$RUN" CONDA_ENV="${EVAL_CONDA_ENV:-evalenv}"
export HF_HOME="${HF_HOME:-/home/$USER/hf_cache}"
mkdir -p "$OUTPUT_DIR"

hours_h200() {  # post-SFT models write 5-15K-token traces x 8 samples; base model is far faster
    case "$1" in
        aime|amc|cn_math_2024) echo 2 ;; gpqa|kaoyan) echo 4 ;; minerva) echo 5 ;; math) echo 6 ;;
        olympiadbench) echo 8 ;; *) echo "unknown benchmark $1" >&2; exit 1 ;;
    esac
}
for B in ${BENCHES:-aime math cn_math_2024 kaoyan amc minerva olympiadbench gpqa}; do
    h=$(hours_h200 "$B") || exit 1
    [ "$GPU" = a100 ] && h=$(( h * 2 > 24 ? 24 : h * 2 ))
    # --chdir=eval: eval_single.sh does `cd $SLURM_SUBMIT_DIR`, so submit from inside eval/ (README).
    jid=$(cd "$REPO/eval" && SB_CHDIR="$REPO/eval" sb --job-name="eval-$RUN-$B" $(gpu_flags 1) --mem=96G \
          --time="$h:00:00" $(dep_flag "${AFTER:-}") eval_single.sh "$B")
    echo "$B: $jid (${h}h)"
done
