---
step: 2
title: Evaluate the base model (gate)
status: next
depends_on: [0]
outputs: [eval/outputs/base/, results/results.md]
cost: ~1 GPU-h (8 parallel 1-GPU jobs)
gate: per-benchmark tolerance + LB6 average within 0.03 of last year's baseline
tags: [step, gate]
---

# Step 2: Evaluate the base model, and the gate

← [Step 1](01-audit-pool.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 3](03-random-baselines.md)

**Goal:** prove the eval environment is sound *before* any training comparison. We evaluate the untrained
Qwen2.5-3B-Instruct on all 8 benchmarks, using the course's unmodified `eval/eval_single.sh` with one job per benchmark.

## How

```bash
launch/eval_model.sh base                       # 8 jobs: cd eval; sbatch eval_single.sh <bench>
# when all 8 finish:
~/.conda/envs/evalenv/bin/python scripts/collect_results.py --gate base
```

## Gate

The numbers must land near last year's baseline row:

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | LB avg |
|---|---|---|---|---|---|---|---|---|
| 0.200 | 0.844 | 0.233 | 0.513 | 0.700 | 0.338 | 0.495 | 0.742 | 0.446 |

> [!WARNING]
> **If the gate prints FAIL, stop.** The eval environment is broken. Fix it before training anything, and record the
> fix in the [decision log](../reference/decision-log.md).

## Results

*(paste the gate table + PASS/FAIL here)*

## Notes

- Compare **Pass@1** (the mean over 8 samples). `Acc` in the logs is pass@8.
- Eval jobs are submitted from a conda-clean environment (`env/clean_conda.sh`); see the
  [ARC guide](../reference/arc-guide.md).
- Spec: [CLAUDE.md, Step 2](../../CLAUDE.md). Benchmarks: [Eval facts](../reference/eval-facts.md).
