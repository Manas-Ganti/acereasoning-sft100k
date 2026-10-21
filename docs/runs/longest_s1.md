---
run: longest_s1
step: 6
status: blocked
train_job:
eval_jobs:
dev_job:
gpu: a100 x8
started:
finished:
wandb:
hf_model:
tags: [run]
---

# Run: longest_s1

> [!WARNING]
> **Dropped 2026-10-20, never built.** Replaced by [short_mid_s1](short_mid_s1.md) (decision log 2026-10-20).

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/longest_s1.json` · **Selection meta:** `data_subsets/longest_s1.meta.json` · **YAML:**
`LLaMA-Factory/yamls/longest_s1.yaml` (identical to the template except `dataset`/`output_dir`)

`pool_idx_sha256`: *(filled in once built)*

> [!NOTE]
> The second smart method, added 2026-10-13 with Manas's approval: the same quality filter and R1-majority rule as
> `full_method`, one response per prompt, then the **15,000 longest traces** by `resp_tokens`. Script:
> `scripts/select_longest.py` (new; existing scripts unchanged). Which smart model is kept is decided by the **dev
> set**, under the rule fixed in advance in the [decision log](../reference/decision-log.md).

> [!WARNING]
> This subset has more training tokens than random (~112M). Expect a longer run than `full_method_s1`. If it hits the
> 23 h short-QOS cap, `slurm/train.slurm` resumes from the newest checkpoint on resubmit. Record the token ratio
> from the meta in the report.

## How to build and submit (on the account that holds `analysis/pool_scores.parquet`)

```bash
cd ~/acereasoning-sft100k && git pull
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/select_longest.py --seed 1 --dry-run     # check the funnel and the token ratio
$PY scripts/select_longest.py --seed 1               # writes the subset + meta + idx
$PY scripts/make_config.py longest_s1
git add data_subsets/longest_s1.meta.json data_subsets/longest_s1.idx.txt && git commit && git push
DRY_RUN=1 EVAL=1 launch/train.sh longest_s1           # preview, then rerun without DRY_RUN
```

On another account: `git pull`, then `$PY scripts/subset_from_idx.py longest_s1 && $PY scripts/make_config.py longest_s1`.

## Selection funnel

*(paste the dry-run output)*

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
