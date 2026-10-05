---
run: <subset name, e.g. random_s1>
step: <3 or 6>
status: queued
train_job:
eval_jobs:
dev_job:
gpu: <h200|a100> x8
started:
finished:
wandb:
hf_model:
tags: [run]
---

# Run: <name>

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/<name>.json` · **Selection meta:** `data_subsets/<name>.meta.json` · **YAML:**
`LLaMA-Factory/yamls/<name>.yaml` (identical to the template except `dataset`/`output_dir`)

## Training
- wall time:
- final train loss:
- checkpoint size (`du -sh`):
- anything unusual:

## Test results (Pass@1)

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | avg(LB6) | boxed_rate |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Dev results

| aime2223 | hmmt25 | math_l5 | gpqa_main |
|---|---|---|---|
| | | | |

## Notes
