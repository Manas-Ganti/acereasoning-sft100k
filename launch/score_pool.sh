#!/bin/bash
# Step 4 -- the critical path. Submits:
#   1. generation array: SHARDS x 1 GPU, k=8 base-model samples per unique math prompt
#   2. grading (CPU, afterok on the whole array) -> analysis/pool_grades.parquet + pool_scores.parquet
#   3. embeddings + k-means (1 GPU, independent)  -> analysis/pool_clusters.parquet + spot-check
# Needs analysis/pool_audit.parquet (Step 1) first.
#   SHARDS=16 launch/score_pool.sh
source "$(dirname "$0")/common.sh"
SHARDS="${SHARDS:-16}"
[ -f "$REPO/analysis/pool_audit.parquet" ] || { echo "run Step 1 (audit) first"; exit 1; }
h=4; [ "$GPU" = a100 ] && h=8
gen=$(CONDA_ENV=evalenv sb --job-name=score-gen $(gpu_flags 1) --cpus-per-task=8 --mem=96G --time="$h:00:00" \
      --array="0-$((SHARDS - 1))" slurm/run.slurm python scripts/score_pool_generate.py --num-shards "$SHARDS")
echo "generation array: $gen ($SHARDS shards)"
grade=$(CONDA_ENV=evalenv sb --job-name=score-grade --partition="$CPU_PARTITION" --qos="${CPU_QOS:-tc_normal_short}" --cpus-per-task=64 --mem=128G \
        --time=06:00:00 --dependency=afterok:"$gen" slurm/run.slurm python scripts/score_pool_grade.py --workers 64)
echo "grading: $grade (after $gen)"
emb=$(CONDA_ENV=myenv sb --job-name=embed $(gpu_flags 1) --cpus-per-task=16 --mem=96G --time=02:00:00 \
      slurm/run.slurm python scripts/embed_cluster.py --k "${K:-100}")
echo "embed+cluster: $emb"
