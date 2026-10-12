---
run: full_method_s1
step: 6
status: queued
train_job: 7958393 (account tml_2026, user manasganti)
eval_jobs: 7958394–7958401 (8 × 2 A100, afterok on 7958393)
dev_job: 7958402 (afterok on 7958393)
gpu: a100 x8
started:
finished:
wandb:
hf_model:
tags: [run]
---

# Run: full_method_s1

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/full_method_s1.json` · **Selection meta:** `data_subsets/full_method_s1.meta.json` · **YAML:**
`LLaMA-Factory/yamls/full_method_s1.yaml` (identical to the template except `dataset`/`output_dir`)

`pool_idx_sha256`: `d733da24ca5ccd65680fa8de44bb4763cc3306ae6ac6de2a07609fc3675bac84`

> [!NOTE]
> The main smart model: clean math only, pass_rate ∈ [0, 0.5] with the R1-majority filter, stratified over 100
> topic clusters (150 rows each). Built 2026-10-12 on Manas's account and submitted the same day with
> `EVAL=1 launch/train.sh full_method_s1`. Eval time limits per benchmark: aime/amc/cn_math 4 h, kaoyan/gpqa 8 h,
> minerva 10 h, math 12 h, olympiadbench 16 h. Racing copies on other accounts follow the decision-log rules.

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
