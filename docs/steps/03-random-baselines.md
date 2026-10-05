---
step: 3
title: Random baselines, two seeds
status: not-started
depends_on: [2]
outputs: [LLaMA-Factory/data/random_s1.json, LLaMA-Factory/data/random_s2.json, saves/qwen25_3b_instruct/random_s{1,2}]
cost: per run, training (time the first one) + ~3 GPU-h eval
tags: [step]
---

# Step 3: Random baselines, two seeds (the noise floor)

← [Step 2](02-base-eval.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 4](04-score-pool.md)

**Goal:** measure how much two *random* 15K subsets differ after training. That spread is the bar every smart
method has to clear. Last year's two random runs scored 0.451 and 0.492, a spread of about 4 points. One random run
is not a baseline.

## How

```bash
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/make_random_subsets.py --seeds 1 2      # -> LLaMA-Factory/data/random_s{1,2}.json + dataset_info.json
$PY scripts/make_config.py random_s1 random_s2      # -> LLaMA-Factory/yamls/random_s{1,2}.yaml (README YAML)
quota                                               # each run peaks ~100 GB of checkpoints
EVAL=1 launch/train.sh random_s1                    # train (8 GPUs) -> 8 eval jobs + dev eval, chained
EVAL=1 launch/train.sh random_s2                    # in parallel only if disk allows
```

Create a run note for each run from the [run template](../templates/run.md), in [runs/](../runs/).

## Frozen setup (the README YAML, never changed after this step)

| Setting | Value |
|---|---|
| DeepSpeed config | `ds_z3_offload_config.json` |
| Attention | flash-attn 2 |
| Learning rate | 5e-6 |
| Epochs | 3 |
| Batch | 1 per GPU × grad-accum 8 × 8 GPUs = 64 |
| Warmup | 0 |
| LR schedule | cosine |
| Cutoff | 16384 |
| Template | `qwen` |

Per-run YAMLs differ only in `dataset` and `output_dir`, and `make_config.py --check` enforces that.

## Done when

Both runs are trained and evaluated, and `collect_results.py` shows the seed spread.

## Results

| run | LB6 avg | all-8 avg | notes |
|---|---|---|---|
| random_s1 | | | |
| random_s2 | | | |
| **seed spread** | | | |

## Notes

- The random subsets sample uniformly from the whole pool, including code and truncated traces. That *is* the
  baseline as the course defines it.
- Time the first run's training and measure one checkpoint (`du -sh .../checkpoint-100`) to update the disk plan.
- Spec: [CLAUDE.md, Step 3](../../CLAUDE.md).
