#!/bin/bash
# README section 4 -- train one subset with the README YAML, then (optionally) chain the evals.
#   launch/train.sh random_s1                 # train only
#   EVAL=1 launch/train.sh random_s1          # train -> 8 eval_single.sh jobs + dev eval (afterok)
#   TIME=23:00:00 GPU=a100 launch/train.sh ...
# Every comparison run uses one full node of 8 GPUs (global batch 1 x 8 x 8 = 64).
source "$(dirname "$0")/common.sh"
RUN="${1:?subset/run name, e.g. random_s1}"
[ -f "$REPO/LLaMA-Factory/data/$RUN.json" ] || { echo "LLaMA-Factory/data/$RUN.json missing"; exit 1; }
[ -f "$REPO/LLaMA-Factory/yamls/$RUN.yaml" ] || { echo "yamls/$RUN.yaml missing: python scripts/make_config.py $RUN"; exit 1; }
jid=$(CONDA_ENV=myenv sb --job-name="sft-$RUN" $(gpu_flags 8) --time="${TIME:-23:00:00}" slurm/train.slurm "$RUN")
echo "train $RUN: $jid"
if [ -n "${EVAL:-}" ]; then
    AFTER=$jid "$REPO/launch/eval_model.sh" "$RUN"
    AFTER=$jid "$REPO/launch/dev_eval.sh" "$RUN"
fi
