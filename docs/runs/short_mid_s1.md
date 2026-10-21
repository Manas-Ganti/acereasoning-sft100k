---
run: short_mid_s1
step: 6
status: running
train_job: 8089882 (account tml_2026, user mrunmayp; 8× A100, 23 h limit)
eval_jobs: 8089883–8089890 (aime, math, cn_math_2024, kaoyan, amc, minerva, olympiadbench, gpqa; 2× A100 each, afterok 8089882)
dev_job: 8089891 (afterok 8089882)
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

`pool_idx_sha256`: `10cd2e1accc194c0d740a75eaef80ccaa6252dc36614345b481d2cf3b8b54848`

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

```
short_mid_s1  (method=short_mid, band=(0.25, 0.75), max_resp_tokens=8192)
   100000  pool
    67432  math
    64907  not truncated (<=16384 tokens)
    64712  balanced oxed{} in final answer
    60648  not proof-like / prose answer
    60586  not contaminated (test)
    60508  not contaminated (dev)
    60504  no repetition / lang-mix / malformed flag
    60504  scored
    59069  drop pass_rate-0 rows whose R1 answer is not the R1 majority
    37980  resp_tokens <= 8192
    37980  in band or a fill tier
    34297  unique prompts (1 response each)
    11571  selected from pass_rate in [0.25, 0.75] (of 11571)
     3429  selected from fill: pass_rate 0 (of 17430)
    15000  selected
```

pass_rate 0 / 0.25 / 0.5 / 0.75: 3,429 / 4,887 / 3,462 / 3,222. Median resp_tokens 4,257; 67,433,589 training tokens
(**0.60×** full_method_s1's ~112M; medium_s1 99.9M). 100 clusters, largest 2.3% (the band is taken whole, so cluster
balance only acts on the fill). Built on mrunmayp 2026-10-20 from the pool_scores.parquet Manas pushed (583c7b4); the
same dry run on Mrunmay's laptop gave the identical funnel.

> [!WARNING]
> Only 11,571 band prompts have a response ≤ 8,192 tokens, so **23% of the subset is pass_rate-0 fill**. Against
> `medium_s1` (band only, no fill) this run therefore changes two things: the length cap and the 3,429 hard
> problems. Caps tried in dry runs only: 10,000 → 1,887 fill (0.67× tokens); 12,000 → 509 (0.74×); 14,000 → 0
> (0.81×). Kept 8,192 as decided (decision log 2026-10-20).

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
