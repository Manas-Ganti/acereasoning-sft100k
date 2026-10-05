---
step: 6
title: Train the smart subset and ablations
status: not-started
depends_on: [3, 5]
outputs: [saves/qwen25_3b_instruct/<run>, eval/outputs/<run>/, work/dev_eval/<run>/]
cost: per run, same as Step 3
tags: [step]
---

# Step 6: Train the smart subset and ablations

← [Step 5](05-selection.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 7](07-compare-submit.md)

**Goal:** train each selection variant with *exactly* the Step 3 setup, so the only difference is the data.

| Run | Isolates |
|---|---|
| `filter_only_s1` | domain + quality filter only |
| `filter_difficulty_s1` | + pass-rate band |
| `full_method_s1` | + cluster stratification |
| `hardest_only_s1` (optional) | pass_rate = 0 only |
| `full_method_s2` (if time allows) | variance on the method side too |

## How

```bash
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/make_config.py filter_only_s1 filter_difficulty_s1 full_method_s1
quota
EVAL=1 launch/train.sh filter_only_s1        # one at a time unless disk allows (~100 GB peak each)
```

Create a run note per run in [runs/](../runs/) from the [run template](../templates/run.md).

## Results

| run | LB6 avg | gpqa | kaoyan | boxed_rate | vs random mean | > seed spread? |
|---|---|---|---|---|---|---|
| filter_only_s1 | | | | | | |
| filter_difficulty_s1 | | | | | | |
| full_method_s1 | | | | | | |

## Notes

- Watch **gpqa** and **kaoyan**: both are multiple-choice, and kaoyan is in Chinese. Pure-math SFT can hurt them.
- Spec: [CLAUDE.md, Step 6](../../CLAUDE.md).
