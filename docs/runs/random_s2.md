---
run: random_s2
step: 3
status: queued
train_job: 7934178 (account tml_2026, user mrunmayp)
eval_jobs: 7934179–7934186 (8 × 2 A100, afterok on 7934178)
dev_job: 7934187 (afterok on 7934178)
gpu: a100 x8
started:
finished:
wandb:
hf_model:
tags: [run]
---

# Run: random_s2

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/random_s2.json` · **Selection meta:** `data_subsets/random_s2.meta.json` · **YAML:**
`LLaMA-Factory/yamls/random_s2.yaml` (identical to the template except `dataset`/`output_dir`)

`pool_idx_sha256`: `b55e6eaa731d444c11b0499ed294c8379673beee34c018edb5f02acab89f9a31`

> [!NOTE]
> Racing copy from Mrunmay's account, submitted 2026-10-10 with `EVAL=1 launch/train.sh random_s2`. Job IDs are mapped
> from submission order (SLURM truncates job names); confirm with `squeue -u $USER -o "%i %j"`. If another
> teammate's copy finishes training first, `scancel` all of these ([decision log](../reference/decision-log.md)).

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
