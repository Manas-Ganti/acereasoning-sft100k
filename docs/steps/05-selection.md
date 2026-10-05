---
step: 5
title: Design the selection
status: not-started
depends_on: [4]
outputs: [LLaMA-Factory/data/<preset>_s<seed>.json, data_subsets/<preset>_s<seed>.meta.json]
cost: CPU, seconds
tags: [step]
---

# Step 5: Design the selection

← [Step 4](04-score-pool.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 6](06-ablations.md)

**Goal:** a deterministic filter-and-sample procedure over `pool_scores.parquet` that yields exactly 15,000 samples.
Each preset adds one ingredient to the previous one, so the ablations isolate it:

| Preset | Adds | Question it answers |
|---|---|---|
| `filter_only` | math only; drop truncated, no `\boxed{}`, ungradeable or proof, contaminated (test + dev), flagged; one R1 response per prompt | "Is it just dropping code and broken samples?" |
| `filter_difficulty` | + pass_rate in [0, 0.5]; drop 0/8 rows whose R1 answer isn't the R1 majority | does difficulty targeting help? |
| `full_method` | + stratify across topic clusters (equal shares, capped by availability) | does topic balance help? |
| `hardest_only` (optional) | pass_rate = 0 only | is "too hard" harmful at 3B? |

## How

```bash
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/select_subset.py full_method --seed 1 --dry-run     # prints the funnel, writes nothing
$PY scripts/select_subset.py filter_only --seed 1
$PY scripts/select_subset.py filter_difficulty --seed 1
$PY scripts/select_subset.py full_method --seed 1
```

Each run writes `LLaMA-Factory/data/<name>.json`, registered the README way. The funnel and composition go to
`data_subsets/<name>.meta.json`, including `sum_total_tokens`, so the training-token difference vs random can be
reported.

## Done when

All presets produce exactly 15,000 rows. Any band or threshold change is justified on the **dev set**, never the test
benchmarks.

## Results

*(paste each preset's funnel and key composition numbers)*

## Notes

- If fewer than 15K unique prompts survive, extra R1 responses fill the gap, and the meta file logs it.
- Spec: [CLAUDE.md, Step 5](../../CLAUDE.md).
