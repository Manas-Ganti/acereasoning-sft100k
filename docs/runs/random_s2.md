---
run: random_s2
step: 3
status: trained (evals pending)
train_job: 7934178 (account tml_2026, user mrunmayp)
eval_jobs: 7934180/84/85/86 (math, minerva, olympiadbench, gpqa); 8004201–04 (aime, amc, cn_math_2024, kaoyan, resubmitted 2026-10-15)
dev_job: 7934187 (afterok on 7934178)
gpu: a100 x8
started: 2026-10-14T07:37
finished: 2026-10-14T13:05 (training)
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
- wall time: 5 h 28 min (2026-10-14 07:37 → 13:05, tc-dgx010); hardware.txt: 8 x NVIDIA A100-SXM4-80GB
- final train loss: 0.6305 (avg over 3 epochs; `all_results.json`), train_runtime 19,442 s, 2.315 samples/s, ~705 steps. ~40% faster than random_s1 on the same data size: node difference (tc-dgx010 vs tc-gpu003), not a config difference
- checkpoint size (`du -sh`): 5.8 GB final model (optimizer checkpoints deleted after DONE)
- anything unusual: tokenizer.json swapped for the base one before its evals started (2026-10-15, fix_tokenizer_for_eval.py). Batch evals aime/amc/cn_math (7934179/83/81) crashed on the 2-GPU fork bug and kaoyan (7934182) on CPU swap; both fixed 2026-10-15, rerun pending.

## Test results (Pass@1)

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | avg(LB6) | boxed_rate |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## Dev results

| aime2223 | hmmt25 | math_l5 | gpqa_main |
|---|---|---|---|
| | | | |

## Notes
