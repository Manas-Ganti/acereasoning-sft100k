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
#   OUT_TAG=h200 BENCHES=olympiadbench LOCAL=1 launch/eval_model.sh base   # -> eval/outputs/base_h200/
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
# eval_single.sh runs `module load Miniconda3; ...; source activate ${CONDA_ENV}` and then a bare `python`.
# That only selects the env if the job starts conda-clean -- see env/clean_conda.sh for why. The env
# is passed by absolute path (verified with launch/test_activation.sh).
clean_conda_env
CONDA_ENV="${EVAL_CONDA_ENV:-$HOME/.conda/envs/evalenv}"
[ -x "$CONDA_ENV/bin/python" ] || { echo "no env at $CONDA_ENV -- run env/setup_envs.sh"; exit 1; }
# OUT_TAG=<tag>: write to eval/outputs/<run>_<tag>/ instead, e.g. a second copy of a run on other
# hardware racing the first (two runs must never share an OUTPUT_DIR). Keep one, discard the other.
export MODEL OUTPUT_DIR="$REPO/eval/outputs/$RUN${OUT_TAG:+_$OUT_TAG}" CONDA_ENV
export HF_HOME="${HF_HOME:-/home/$USER/hf_cache}" PYTHONNOUSERSITE=1
mkdir -p "$OUTPUT_DIR"

hours_h200() {  # post-SFT models write 5-15K-token traces x 8 samples; base model is far faster
    case "$1" in
        aime|amc|cn_math_2024) echo 2 ;; gpqa|kaoyan) echo 4 ;; minerva) echo 5 ;; math) echo 6 ;;
        olympiadbench) echo 8 ;; *) echo "unknown benchmark $1" >&2; exit 1 ;;
    esac
}
if [ -n "${LOCAL:-}" ]; then
    # LOCAL=1: run the benchmarks one after another on the GPU(s) of an allocation you are already in
    # (e.g. an interactive session), instead of queueing one batch job per benchmark. Same unmodified
    # eval_single.sh, same conda-clean environment; benchmarks that already have results are skipped.
    [ -n "${SLURM_JOB_ID:-}" ] || { echo "LOCAL=1 must run inside a GPU allocation (salloc / interact)"; exit 1; }
    export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
    for B in ${BENCHES:-aime math cn_math_2024 kaoyan amc minerva olympiadbench gpqa}; do
        if find "$OUTPUT_DIR" -path "*/$B/test_*.jsonl" 2>/dev/null | grep -q .; then echo "== $B: done already, skipping"; continue; fi
        echo "== $B"
        (cd "$REPO/eval" && SLURM_SUBMIT_DIR="$REPO/eval" bash eval_single.sh "$B") | grep -E "^(correct cnt|Acc|Pass@1)"
    done
    exit 0
fi

# EVAL_GPUS: eval.py runs tensor-parallel over every visible GPU. With 1 GPU, long n=8 traces overflow vLLM's
# 4 GiB default CPU swap ("Aborted due to the lack of CPU swap space", base OlympiadBench 2026-10-09); 2 GPUs
# double the KV cache and the swap. Trained models write long traces, so they default to 2.
if [ "$RUN" = base ]; then EVAL_GPUS="${EVAL_GPUS:-1}"; else EVAL_GPUS="${EVAL_GPUS:-2}"; fi
for B in ${BENCHES:-aime math cn_math_2024 kaoyan amc minerva olympiadbench gpqa}; do
    h=$(hours_h200 "$B") || exit 1
    [ "$GPU" = a100 ] && h=$(( h * 2 > 24 ? 24 : h * 2 ))
    # The base model writes ~1K-token answers: minutes per benchmark. Short limits backfill much sooner.
    [ "$RUN" = base ] && { h=1; [ "$B" = olympiadbench ] || [ "$B" = math ] && h=2; }
    # --chdir=eval: eval_single.sh does `cd $SLURM_SUBMIT_DIR`, so submit from inside eval/ (README).
    jid=$(cd "$REPO/eval" && SB_CHDIR="$REPO/eval" sb --job-name="eval-$RUN-$B" $(gpu_flags "$EVAL_GPUS") --mem=96G \
          --time="$h:00:00" $(dep_flag "${AFTER:-}") eval_single.sh "$B")
    echo "$B: $jid (${h}h, $EVAL_GPUS GPU)"
done
