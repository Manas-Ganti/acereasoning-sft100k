---
run: random_s1
step: 3
status: trained (evals pending)
train_job: 7934168 (account tml_2026, user mrunmayp)
eval_jobs: 7999722–7999729 (resubmitted 2026-10-15; first set 7934169–76 crashed on the tokenizer)
dev_job: 7934177 (afterok on 7934168)
gpu: a100 x8
started: 2026-10-13T16:02
finished: 2026-10-13T23:46 (training)
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
- wall time: 7 h 44 min (2026-10-13 16:02 → 23:46, tc-gpu003); hardware.txt: 8 x NVIDIA A100-SXM4-80GB
- final train loss: 0.6331 (avg over 3 epochs; `all_results.json`), train_runtime 27,547 s, 1.634 samples/s, ~705 steps
- checkpoint size (`du -sh`): 5.8 GB final model (optimizer checkpoints deleted after DONE)
- anything unusual: all 8 test evals (7934169–76) crashed at tokenizer load ("untagged enum ModelWrapper"; SLURM showed COMPLETED because of `tee`). Fixed 2026-10-15 with `scripts/fix_tokenizer_for_eval.py`; evals resubmitted as 7999722–29.

## Test results (Pass@1)

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | avg(LB6) | boxed_rate |
|---|---|---|---|---|---|---|---|---|---|
| 0.0625 | 0.6492 | 0.0917 | 0.2563 | 0.3719 | | | 0.2645 | | |

Acc (pass@8) so far: aime 0.2333, math 0.8640, cn_math_2024 0.3333, kaoyan 0.6382, amc 0.6750, gpqa 0.7626. aime, amc and cn_math_2024 ran 2026-10-15 in a 2× A100
interactive session (job 8000314, tc-gpu003, `LOCAL=1`); their batch copies were cancelled. math: batch job 7999723 (2 h 06 min, tc-gpu001, finished 2026-10-17 11:23). Base model math: Pass@1 0.646, Acc 0.854. kaoyan: batch job 7999725 (1 h 58 min, tc-dgx001, finished 2026-10-17; base 0.220 / 0.528). gpqa: batch job 7999729 (1 h 48 min, tc-gpu001; base 0.289 / 0.707), the rerun of the copy that crashed on swap.

## Dev results

| aime2223 | hmmt25 | math_l5 | gpqa_main |
|---|---|---|---|
| | | | |

## Notes
