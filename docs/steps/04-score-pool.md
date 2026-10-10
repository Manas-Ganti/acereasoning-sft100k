---
step: 4
title: Score every prompt in the pool
status: running
depends_on: [1]
outputs: [analysis/pool_scores.parquet, analysis/pool_grades.parquet, analysis/pool_clusters.parquet, analysis/clusters_spotcheck.md]
cost: ~6-10 GPU-h generation + CPU grading + <1 GPU-h embeddings
tags: [step, critical-path]
---

# Step 4: Score every prompt in the pool (critical path)

← [Step 3](03-random-baselines.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 5](05-selection.md)

**Goal:** give every math sample the signals the smart selection needs:

| Column | Meaning |
|---|---|
| `pass_rate` | Qwen-3B answers the prompt 8 times (temp 0.6, top-p 0.95, eval's system prompt and chat template). This is the fraction that matches **R1's boxed answer**, graded by `eval/utils/grader.py`. 0 = too hard, 1 = already solved. |
| `r1_agreement` | for prompts with several R1 responses: do they agree on the answer? Low agreement means R1's label is probably noisy. |
| `cluster_id` | k-means (k=100) over prompt embeddings (bge-base), used to balance topics |
| `flags` | carried over from the [audit](01-audit-pool.md) |

## How

```bash
launch/score_pool.sh          # needs analysis/pool_audit.parquet (Step 1)
# submits: generation array (16 x 1 GPU) -> grading (CPU, afterok) ; embeddings + k-means (1 GPU, parallel)
```

Then **read `analysis/clusters_spotcheck.md`**. The clusters should be topics (geometry, number theory, …), not
formatting artefacts.

## Done when

`analysis/pool_scores.parquet` has `pass_rate`, `r1_agreement` and `cluster_id`, and the cluster spot-check looks
sane.

## Results

*(fill in: pass_rate histogram, # prompts at 0/8, r1_agreement summary, cluster size range, spot-check verdict)*

## Notes

- Scoring uses `max_tokens` 8192, not 32768, to save cost. Samples that hit the cap count as failures, and
  `base_cap_frac` records how often that happened.
- `pass_rate` is per **row**: each R1 response is graded against its own answer.
- Spec: [CLAUDE.md, Step 4](../../CLAUDE.md).
