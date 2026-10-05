#!/bin/bash
# 5-minute CPU job: does eval_single.sh's `source activate ${CONDA_ENV}` select our env inside a real
# batch job, for a bare name vs an absolute path? Read logs/slurm/test-activation-<id>.out.
source "$(dirname "$0")/common.sh"
jid=$(sb --job-name=test-activation --partition="$CPU_PARTITION" --qos="${CPU_QOS:-tc_normal_short}" \
      slurm/test_activation.slurm)
echo "submitted $jid -> logs/slurm/test-activation-$jid.out"
