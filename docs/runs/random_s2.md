---
run: random_s2
step: 3
status: trained (evals pending)
train_job: 7934178 (account tml_2026, user mrunmayp)
eval_jobs: 7934184 (minerva, done); 8004201–04 (aime, amc, cn_math_2024, kaoyan, resubmitted 2026-10-15); 8039875–77 (math, olympiadbench, gpqa, resubmitted 2026-10-17)
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
- 2026-10-17: aime (8004201, 30 min) Pass@1 0.0792, Acc 0.2333 (base 0.067 / 0.167); amc (8004202, 20 min) Pass@1 0.3594, Acc 0.7000 (base 0.412 / 0.650). First jobs to run with the preempt hook. cn_math_2024 (8004203, 22 min) Pass@1 0.1333, Acc 0.3667 (base 0.133 / 0.400). gpqa (8039877, 1 h 32 min, rerun after the scheduler assert) Pass@1 0.2689, Acc 0.7677 (base 0.289 / 0.707). kaoyan (8004204, 2 h 26 min, rerun after the swap crash) Pass@1 0.2563, Acc 0.6080 (base 0.220 / 0.528).
- 2026-10-17: minerva (7934184, 2 h 28 min, tc-gpu004) finished: Pass@1 0.2767, Acc 0.4522 (base: 0.303 / 0.489). math (7934180, 1 h 21 min), olympiadbench (7934185, 1 h 41 min) and gpqa (7934186, 2 h 03 min) show COMPLETED, but their logs have no `Acc:` line: they crashed on the vLLM scheduler `assert len(seqs) == 1` (gpqa at 111/198, olympiadbench at 137/675); fix `env/vllm_preempt_hook.sh`; resubmitted as 8039875/76/77, logs moved to `eval/outputs/random_s2_crashed/log_*_schedassert.txt`.
- 2026-10-18: math (8039875, started 13:13) finished: Pass@1 0.6502, Acc 0.8480 (base 0.646 / 0.854). Duplicate 4 h copy 8051910 cancelled. olympiadbench: 9 h copy 8051763 (8 h copy 8052023 and old 16 h 8039876 cancelled) TIMEOUT mid-generation at 485/675; rerun 8066504 (16 h) running since 2026-10-19 23:02.

## Test results (Pass@1)

| aime | math | cn_math_2024 | kaoyan | amc | minerva | olympiadbench | gpqa | avg(LB6) | boxed_rate |
|---|---|---|---|---|---|---|---|---|---|
| 0.0792 | 0.6502 | 0.1333 | 0.2563 | 0.3594 | 0.2767 | | 0.2689 | | |

## Dev results

| aime2223 | hmmt25 | math_l5 | gpqa_main |
|---|---|---|---|
| | | | |

## Notes
