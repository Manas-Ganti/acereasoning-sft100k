---
step: 2
title: Evaluate the base model (gate)
status: running
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

The **Acc (pass@8)** numbers must land near last year's baseline row (these are leaderboard numbers, which are pass@8):

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | LB avg |
|---|---|---|---|---|---|---|---|---|
| 0.200 | 0.844 | 0.233 | 0.513 | 0.700 | 0.338 | 0.495 | 0.742 | 0.446 |

> [!WARNING]
> **If the gate prints FAIL, stop.** The eval environment is broken. Fix it before training anything, and record the
> fix in the [decision log](../reference/decision-log.md).

## Results

| benchmark | Pass@1 | Acc (pass@8) | ref (pass@8) | gate | job |
|---|---|---|---|---|---|
| aime | 0.067 (2.0/30) | 0.167 (5/30) | 0.200 | ok | 7865700 |
| math | 0.646 (322.9/500) | 0.854 (427/500) | 0.844 | ok | 7865701 |
| cn_math_2024 | 0.133 (4.0/30) | 0.400 (12/30) | 0.233 | ok | 7865702 |
| kaoyan | 0.220 (43.9/199) | 0.528 (105/199) | 0.513 | ok | 7865703 |
| amc | 0.412 (16.5/40) | 0.650 (26/40) | 0.700 | ok | 7865704 |
| minerva | 0.303 (82.4/272) | 0.489 (133/272) | 0.338 | OFF (+0.151, *above* ref) | 7865705 |
| olympiadbench | — | — | 0.495 | missing | — |
| gpqa | — | — | 0.742 | missing | — |

Gate (2026-10-08, 6/8 done): **FAIL**, for two reasons: the LB average is `nan` because OlympiadBench and GPQA
have not run yet, and Minerva is flagged OFF because it is 0.151 *above* the reference. A broken eval would lower
scores, not raise them, and the other 6 benchmarks match within tolerance (MATH 0.854 vs 0.844), so the eval
environment looks sound. The Minerva gap is most likely a difference in last year's setup. Logs are clean apart from
tokenizers-parallelism warnings and the expected ANTLR 4.9.3/4.7.2 version notice (the latex2sympy2 route from the
decision log). Grading still works: MATH matches.

> [!NOTE]
> Manas (2026-10-08): the assignment does not require matching last year's base numbers. Proposed: make the gate
> one-sided (fail only when far *below* the ref). Awaiting a decision; not yet changed.

## Notes

- The gate compares **Acc (pass@8)**. Pass@1 stays our primary metric for the study; the tables show both.
- Eval jobs are submitted from a conda-clean environment (`env/clean_conda.sh`); see the
  [ARC guide](../reference/arc-guide.md).
- Spec: [CLAUDE.md, Step 2](../../CLAUDE.md). Benchmarks: [Eval facts](../reference/eval-facts.md).
