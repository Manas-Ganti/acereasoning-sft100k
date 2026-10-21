---
run: short_mid_s1
step: 6
status: not-started
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

# Run: short_mid_s1

← [STATUS](../STATUS.md) · [Runs index](../runs/README.md)

**Subset:** `LLaMA-Factory/data/short_mid_s1.json` · **Selection meta:** `data_subsets/short_mid_s1.meta.json` · **YAML:**
`LLaMA-Factory/yamls/short_mid_s1.yaml` (identical to the template except `dataset`/`output_dir`)

`pool_idx_sha256`: *(filled in once built)*

> [!NOTE]
> Third smart method, added 2026-10-20 with Manas's approval; replaces `longest_s1`
> ([decision log](../reference/decision-log.md)). Script: `scripts/select_short_mid.py` (new; existing scripts
> unchanged). Same quality filter and R1-majority rule as `full_method`, then:
> 1. `resp_tokens` ≤ 8,192 (the cap Step 4 scored pass_rate with)
> 2. pass_rate in [0.25, 0.75] (Qwen-3B solved 1–3 of 4)
> 3. one response per prompt: majority-agreeing, then the **shortest**
> 4. cluster water-filling to 15,000
>
> If the band runs short, it fills in this fixed order: pass_rate 0 (≤ 8K tokens), then pass_rate 1.0. The meta
> records the tier counts. Against `medium_s1` (same band and topic balance, no length cap), this run isolates the
> length cap.

> [!WARNING]
> Fewer training tokens than random/full_method (~112M). Record the ratio from the dry run in the report. Tested on
> synthetic scores only (deterministic: two runs gave identical rows). Check the real funnel with `--dry-run` first.
> If it stops with "only N rows available", the fill tiers are exhausted: rerun with a higher
> `--max-resp-tokens` (e.g. 10000) and note it here.

## How to build and submit (on the account that holds `analysis/pool_scores.parquet`)

```bash
cd ~/acereasoning-sft100k && git pull
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/select_short_mid.py --seed 1 --dry-run   # check the funnel, fill rows and token ratio
$PY scripts/select_short_mid.py --seed 1             # writes the subset + meta + idx
$PY scripts/make_config.py short_mid_s1
git add data_subsets/short_mid_s1.meta.json data_subsets/short_mid_s1.idx.txt && git commit && git push
DRY_RUN=1 EVAL=1 launch/train.sh short_mid_s1         # preview, then rerun without DRY_RUN
```

On another account: `git pull`, then `$PY scripts/subset_from_idx.py short_mid_s1 && $PY scripts/make_config.py short_mid_s1`.

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
