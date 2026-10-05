#!/bin/bash
#SBATCH --job-name=run
#SBATCH --nodes=1
#SBATCH --ntasks=1
# Generic runner; resources come from the launcher (launch/cpu.sh, launch/score_pool.sh, launch/embed.sh).
#   sbatch ... slurm/run.slurm python scripts/<x>.py [args]
# A leading `python` is replaced by the env's interpreter ($PY), never resolved through PATH.
set -eo pipefail
REQUIRE_ENV="${REQUIRE_ENV:-}" source "$REPO/env/arc_env.sh"
cmd=("$@")
[ "${cmd[0]}" = python ] && cmd[0]="$PY"
echo "[run] ${cmd[*]}"
"${cmd[@]}"
