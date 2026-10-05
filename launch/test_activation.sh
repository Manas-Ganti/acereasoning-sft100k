#!/bin/bash
# 5-minute CPU job: does eval_single.sh's `source activate ${CONDA_ENV}` select our env inside a real
# batch job, for a bare name vs an absolute path? Read logs/slurm/test-activation-<id>.out.
#   CLEAN=0 launch/test_activation.sh   submits WITHOUT cleaning (reproduces the bug)
source "$(dirname "$0")/common.sh"
[ "${CLEAN:-1}" = 1 ] && clean_conda_env
jid=$(sb --job-name=test-activation --partition="$CPU_PARTITION" --qos="${CPU_QOS:-tc_normal_short}" \
      slurm/test_activation.slurm)
echo "submitted $jid -> logs/slurm/test-activation-$jid.out"
