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

Run 2026-10-09 → 10-10 (Manas's account): score-gen array 7927684 (16 × 1 A100, k=4, all COMPLETED; ~1.1 h per
shard, shard 2 2h50; **≈20.5 A100 GPU-h**), score-grade 7927689 (CPU, 1h35), embed 7927690 (1 A100, 4.5 min).
Sanity check (shard 0, chunk 0, 2,000 prompts): median 750 generated tokens, p90 1,314, 1.8% hit the 8K cap, 1.8% empty.

| pass_rate (k=4), 67,432 math rows | value |
|---|---|
| mean | 0.257 |
| median | **0** (more than half the rows: 0/4) |
| 75th percentile | 0.5 |

**The pool is hard for a 3B model**: most of it is AoPS-style OpenMathReasoning. This is a finding, not something we tune.

**r1_agreement.** The summary in the grade log (median 0.5, 28,372 rows) **includes code rows**, whose empty answers
never compare equal. Use the math-only numbers: 14,758 answered math rows with >1 R1 response, mean 0.917, median
1.0. Spot-check of 15 disagreeing prompts: about 6 are genuine (`40 | 140`, `14 | 10`, `184 | 93`), about 7 are
notation (`n≥4 and n≠5` vs `n=4 or n≥6`, `a√3` vs `A√3`, `60°,60°,60°` vs `60°`), and 2 are partial-vs-full
answers. The R1-majority filter is kept as planned (decision log 2026-10-12); it removes 1,435 rows.

**Clusters.** k=100 over 59,702 unique math prompts (bge-base-en-v1.5): sizes 181–1,242 (median 568). The largest are
clean topics: functional equations, probability, triangle geometry, smallest-integer problems, max/min inequalities,
conics, angle chasing, sets, grids/tilings, circles. No formatting-artefact clusters. Geometry spans several clusters.

## Notes

- Scoring uses `max_tokens` 8192, not 32768, to save cost. Samples that hit the cap count as failures, and
  `base_cap_frac` records how often that happened.
- `pass_rate` is per **row**: each R1 response is graded against its own answer.
- Spec: [CLAUDE.md, Step 4](../../CLAUDE.md).
