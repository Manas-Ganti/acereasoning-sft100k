---
run: random_s1
step: 3
status: queued
train_job: 7934168 (account tml_2026, user mrunmayp)
eval_jobs: 7934169–7934176 (8 × 2 A100, afterok on 7934168)
dev_job: 7934177 (afterok on 7934168)
gpu: a100 x8
started:
finished:
wandb:
hf_model:
tags: [run]
---

# Run: random_s1

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/random_s1.json` · **Selection meta:** `data_subsets/random_s1.meta.json` · **YAML:**
`LLaMA-Factory/yamls/random_s1.yaml` (identical to the template except `dataset`/`output_dir`)

`pool_idx_sha256`: `6212267ef1b14125d03a1c2b982eefcf65d75e25666e8c3a1c69d1a345aa8898`

> [!NOTE]
> Racing copy from Mrunmay's account, submitted 2026-10-10 with `EVAL=1 launch/train.sh random_s1`. Job IDs are mapped
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
