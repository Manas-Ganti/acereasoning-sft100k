#!/bin/bash
#SBATCH --job-name=sft
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=0
# README section 4 run_training.sh, with resources from launch/train.sh (8 GPUs instead of 1, a
# long wall time instead of 1 h -- both known issues of the sample script):
#   module load Miniconda3; module load CUDA/12.6.0; source activate myenv
#   cd LLaMA-Factory; FORCE_TORCHRUN=1 llamafactory-cli train yamls/<run>.yaml
# Additions: resume from the newest checkpoint-* if the job was cut off; DONE marker on success.
set -eo pipefail
RUN="$1"
source "$REPO/env/arc_env.sh"
"$PY" scripts/make_config.py --check "$RUN"

# All comparison runs must share the global batch (per_device 1 x grad_accum 8 x GPUs).
NGPU=$(nvidia-smi -L | wc -l)
[ "$NGPU" = "${EXPECTED_GPUS:-8}" ] || { echo "[train] got $NGPU GPUs, expected ${EXPECTED_GPUS:-8}"; exit 1; }

cd "$REPO/LLaMA-Factory"
OUT="saves/qwen25_3b_instruct/$RUN"
[ -f "$OUT/DONE" ] && { echo "[train] $RUN already finished"; exit 0; }
mkdir -p "$OUT"
EXTRA=""
LAST=$(ls -d "$OUT"/checkpoint-* 2>/dev/null | sort -V | tail -1 || true)
[ -n "$LAST" ] && { EXTRA="resume_from_checkpoint=$LAST"; echo "[train] resuming from $LAST"; }

FORCE_TORCHRUN=1 llamafactory-cli train "yamls/$RUN.yaml" $EXTRA 2>&1 | tee -a "$OUT/train.log"

ls "$OUT"/*.safetensors >/dev/null 2>&1 && [ -f "$OUT/tokenizer_config.json" ] \
    || { echo "[train] FATAL: no final model in $OUT"; exit 1; }
echo "$NGPU x $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" > "$OUT/hardware.txt"
rm -rf "$OUT"/checkpoint-*      # optimizer-state checkpoints; the final model is kept
date > "$OUT/DONE"
echo "[train] $RUN done -> LLaMA-Factory/$OUT"
