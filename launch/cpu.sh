#!/bin/bash
# CPU job (default env evalenv; CONDA_ENV=myenv to change):
#   launch/cpu.sh python scripts/audit_pool.py
#   TIME=02:00:00 CPUS=64 launch/cpu.sh python scripts/score_pool_grade.py --workers 64
source "$(dirname "$0")/common.sh"
jid=$(CONDA_ENV="${CONDA_ENV:-evalenv}" sb --job-name="cpu-$(basename "${2:-job}" .py)" --partition="$CPU_PARTITION" \
      --cpus-per-task="${CPUS:-32}" --mem="${MEM:-128G}" --time="${TIME:-04:00:00}" \
      $(dep_flag "${AFTER:-}") slurm/run.slurm "$@")
echo "submitted $jid  (log: logs/slurm/cpu-*-$jid.out)"
