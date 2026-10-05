#!/bin/bash
# Dev-set eval (used for any selection / hyperparameter decision; never the 8 test sets).
#   launch/dev_eval.sh base
#   AFTER=<train jobid> launch/dev_eval.sh full_method_s1
source "$(dirname "$0")/common.sh"
RUN="${1:?run name}"
if [ "$RUN" = base ]; then MODEL="Qwen/Qwen2.5-3B-Instruct"; else MODEL="$REPO/LLaMA-Factory/saves/qwen25_3b_instruct/$RUN"; fi
[ -d "$REPO/dev/data" ] || { echo "dev/ not built: run scripts/build_dev_set.py"; exit 1; }
h=6; [ "$GPU" = a100 ] && h=12
jid=$(SFT_ENV=evalenv sb --job-name="dev-$RUN" $(gpu_flags 1) --time="$h:00:00" $(dep_flag "${AFTER:-}") \
      slurm/dev_eval.slurm "$MODEL" "$RUN")
echo "dev eval $RUN: $jid"
