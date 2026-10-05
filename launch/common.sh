# Sourced by launch/*.sh. All scheduling knobs live here and are passed as sbatch CLI flags.
#
#   GPU=h200|a100        (default h200)      ACCOUNT=<slurm account> (default tml_2026)
#   QOS=<name>|none      (default tc_<gpu>_normal_short)
#   CONDA_ENV            per job: evalenv (eval, audit, scoring, selection) or myenv (training, embeddings)
#   MAIL_USER=<address>  (optional)          CPU_PARTITION (default normal_q), CPU_QOS (default tc_normal_short)
#   DRY_RUN=1            print sbatch lines, submit nothing
#
# "short" QOS = highest priority, 1-day cap (arc_runbook.md section 5). Never fall back to the
# preemptable partitions. Always an explicit --mem on partial-node jobs (--mem=0 can't backfill).
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ACCOUNT="${ACCOUNT:-tml_2026}"
GPU="${GPU:-h200}"
CPU_PARTITION="${CPU_PARTITION:-normal_q}"
case "$GPU" in
    h200) PARTITION=h200_normal_q; DEFAULT_QOS=tc_h200_normal_short ;;
    a100) PARTITION=a100_normal_q; DEFAULT_QOS=tc_a100_normal_short ;;
    *) echo "GPU must be h200 or a100" >&2; exit 2 ;;
esac
QOS="${QOS:-$DEFAULT_QOS}"
mkdir -p "$REPO/logs/slurm"
source "$REPO/env/clean_conda.sh"

# sb <sbatch args...>  -> prints the job id
sb() {
    local args=(--parsable --account="$ACCOUNT" --chdir="${SB_CHDIR:-$REPO}" --export="ALL,REPO=$REPO,CONDA_ENV=${CONDA_ENV:-myenv}${REQUIRE_ENV:+,REQUIRE_ENV=$REQUIRE_ENV}"
                --output="$REPO/logs/slurm/%x-%j.out")
    [ -n "${MAIL_USER:-}" ] && args+=(--mail-user="$MAIL_USER" --mail-type=END,FAIL,TIME_LIMIT_80)
    if [ -n "${DRY_RUN:-}" ]; then
        echo "sbatch ${args[*]} $*" >&2
        echo "DRY$RANDOM"
    else
        sbatch "${args[@]}" "$@"
    fi
}

gpu_flags() {  # gpu_flags <n gpus>
    local q=""; [ "$QOS" != none ] && q="--qos=$QOS"
    echo "--partition=$PARTITION $q --gres=gpu:$GPU:$1"
}

dep_flag() {   # dep_flag <jobid or empty>
    [ -n "$1" ] && echo "--dependency=afterok:$1"
}
