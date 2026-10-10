---
title: STATUS
current_step: 3
phase: Step 3 queued (random_s1/s2 training); Step 4 scoring running
last_updated: 2026-10-10
updated_by: Mrunmay + Claude
tags: [status]
---

# STATUS: where the project is

> [!IMPORTANT]
> **Read this first, update it last.** Anyone, human or agent, who submits a job, gets a result, makes a decision or
> hits a blocker updates this file before stopping. Keep it short and current, and move detail into the step notes.
> Protocol: [CLAUDE.md, "Start here"](../CLAUDE.md).

## Now

Setup is complete on ARC: both envs are built and verified, the pool and base model are downloaded, and the dev set
is built. Activation inside batch jobs was verified with `launch/test_activation.sh`, which passed for both envs.
Step 1 audit done. Step 2: all 8 base-eval benchmarks done (OlympiadBench on 1× H200, job 7921791). Step 4 scoring is running.
**Step 3 queued (2026-10-10):** `random_s1` / `random_s2` training submitted from Mrunmay's account (jobs 7934168 /
7934178, 8× A100, evals + dev eval chained). Subset hashes are in the [Step 3 note](steps/03-random-baselines.md).

**Base model (Qwen2.5-3B-Instruct), final 2026-10-10:**

| benchmark | Pass@1 | Acc (pass@8) | last year (pass@8) | gate |
|---|---|---|---|---|
| aime | 0.067 | 0.167 | 0.200 | ok |
| math | 0.646 | 0.854 | 0.844 | ok |
| cn_math_2024 | 0.133 | 0.400 | 0.233 | ok |
| kaoyan | 0.220 | 0.528 | 0.513 | ok |
| amc | 0.412 | 0.650 | 0.700 | ok |
| minerva | 0.303 | 0.489 | 0.338 | OFF (+0.151, *above* ref) |
| olympiadbench | 0.277 | 0.492 | 0.495 | ok (1× H200 rerun) |
| gpqa | 0.289 | 0.707 | 0.742 | ok (−0.035, tol ±0.093) |

> [!NOTE]
> The gate prints FAIL only because scores land *above* the reference (Minerva, CN Math).
> The eval environment looks sound: logs are clean and MATH matches within 0.01. Manas: matching last year's base is
> not required. A one-sided gate is proposed but not adopted yet. Details: [Step 2](steps/02-base-eval.md#results).

**Resume here:**
1. **Step 3:** Mrunmay's copies are queued (7934168 / 7934178). Subsets + YAMLs are on `main` (`6332a08`).
   Other teammates racing: `git pull`, generate, check your hashes against the
   [Step 3 note](steps/03-random-baselines.md), submit. When one copy finishes training, cancel the others.
   Time the first run and `du -sh` a checkpoint (disk plan).
2. **Step 4:** watch jobs 7927684 / 7927689 / 7927690; fill in the Step 4 results when grading and clustering finish.
3. Decide the training GPU plan (8 vs 4 GPUs per run) from `sinfo`/`sshare`/Owl/Falcon availability.
4. Manas: decide on the one-sided Step 2 gate (not blocking).

## Step board

| # | Step | Status | Gate / key result | Note |
|---|---|---|---|---|
| 0 | Setup | ✅ done | `check_envs` + batch activation test pass | [00-setup](steps/00-setup.md) |
| 1 | Audit pool | ✅ done | 67% math / 33% code; 3.7% truncated; 91 contaminated rows (AMC 4/40) | [01-audit-pool](steps/01-audit-pool.md) |
| 2 | Base eval + gate | ✅ eval done (gate decision open) | all 8 in; LB6 pass@8 0.544 vs 0.503; FAIL only from scores *above* ref (Minerva, CN Math) | [02-base-eval](steps/02-base-eval.md) |
| 3 | Random ×2 | 🔄 queued (7934168 / 7934178) | seed spread = the bar | [03-random-baselines](steps/03-random-baselines.md) |
| 4 | Score pool | 🔄 running (k=4, 16 shards) | shard sanity check healthy; ~18 A100 GPU-h | [04-score-pool](steps/04-score-pool.md) |
| 5 | Selection | ⬜ not started (needs Step 4) | — | [05-selection](steps/05-selection.md) |
| 6 | Ablations | ⬜ not started | — | [06-ablations](steps/06-ablations.md) |
| 7 | Compare + submit | ⬜ not started | deadline **Oct 20** | [07-compare-submit](steps/07-compare-submit.md) |

Legend: ⬜ not started · ⏭️ next · 🔄 running · ✅ done · ⛔ blocked / gate failed

## Running jobs

| Job ID | What | Submitted | Expected | Log |
|---|---|---|---|---|
| 7865518–25 | base eval on H200 | 2026-10-05 | cancelled (4-day queue) | — |
| (AIME) | base eval aime, A100 | 2026-10-05 | ✅ done: Pass@1 0.067, Acc 0.167 | `eval/outputs/base/log_aime.txt` |
| 7865701–05 | base eval math, cn_math, kaoyan, amc, minerva | 2026-10-05 | ✅ done | `logs/slurm/eval-base-*.out` |
| 7865706–07 | base eval olympiadbench, gpqa | 2026-10-05 | superseded: GPQA done interactively, OlympiadBench by 7921791 (1× H200) | — |
| 7927684_[0-15] | Step 4 score-gen, k=4, 16 × 1 A100 | 2026-10-09 | shards 0–1 done (~1.1 h each → ~18 A100 GPU-h total) | `work/scores/gen/` |
| 7927689 | Step 4 score-grade (CPU, afterok on 7927684) | 2026-10-09 | after all shards | — |
| 7927690 | Step 4 embed + k-means (1 A100) | 2026-10-09 | queued | `analysis/clusters_spotcheck.md` |
| 7934168 | Step 3 train `random_s1`, 8× A100 (mrunmayp) | 2026-10-10 | ≤23 h once started | `LLaMA-Factory/saves/qwen25_3b_instruct/random_s1/train.log` |
| 7934169–77 | `random_s1` 8 evals (2× A100 each) + dev eval, afterok 7934168 | 2026-10-10 | after training | [run note](runs/random_s1.md) |
| 7934178 | Step 3 train `random_s2`, 8× A100 (mrunmayp) | 2026-10-10 | ≤23 h once started | `LLaMA-Factory/saves/qwen25_3b_instruct/random_s2/train.log` |
| 7934179–87 | `random_s2` 8 evals (2× A100 each) + dev eval, afterok 7934178 | 2026-10-10 | after training | [run note](runs/random_s2.md) |

## Next actions

- [x] Step 1: audit, see [results](steps/01-audit-pool.md#results)
- [ ] Spot-check near-miss contamination (contam_score 0.3–0.5) before Step 5
- [x] Step 2: all 8 base benchmarks done (one-sided gate decision still open)
- [x] Step 4: submitted 2026-10-09 (jobs 7927684 / 7927689 / 7927690)
- [x] Step 3: `random_s1`/`random_s2` generated (15,000 rows each, YAML check ok) and submitted (Mrunmay)
- [x] Step 3: subset commit `6332a08` pushed from ARC (SSH key set up on Mrunmay's ARC account)
- [ ] Check `quota` before any training: each run peaks at about 100 GB of checkpoints

## Blockers / open questions

- **Disk for training (2026-10-10):** ~118 GB free on Manas's `/home` vs ~100 GB peak per run. Decide where training
  runs live (teammates' quota / scratch / `save_only_model`). Two teammates are joining the project.

- **GPU scarcity:** on 2026-10-05, 1-GPU A100 batch jobs were estimated 4–5 days out, and H200 was worse. 8-GPU training
  may not schedule in time. Options: 4 GPUs with grad-accum 16 (same global batch 64; GA is a README "tweak" field),
  or Owl B200 / Falcon. Undecided: needs `sinfo`/`sshare` numbers and Manas's decision.
- Disk: `/home` had ~151 GB free before two old repos were deleted, and the quota display updates later. Re-check
  `quota` before Step 3.

## Change log (newest first)

- **2026-10-10**: Step 3 submitted from Mrunmay's account: `random_s1` train 7934168 (evals 7934169–76, dev 7934177),
  `random_s2` train 7934178 (evals 7934179–86, dev 7934187); 8× A100, ≤~184 A100 GPU-h each for training. Hashes
  s1 `6212267e…`, s2 `b55e6eaa…`. Mrunmay's setup finished: `check_envs` ALL CHECKS PASSED, pool 100,000 rows, dev
  set built (GPQA needed `HF_HOME=/home/$USER/hf_cache` exported in the login shell).

- **2026-10-10**: Mrunmay's evalenv: activation test passes for both envs, but pyarrow 26 (pulled in by unpinned
  `datasets` 5.0.1) needs NumPy 2 next to vllm's 1.26.4, so `fetch_data.py`, `build_dev_set.py` and `eval/` fail.
  Fix: `bash env/fix_evalenv_arrow.sh` (decision log). `check_envs.sh` now catches it.

- **2026-10-10**: Docs synced to the real state: current step is 3 (next, nothing submitted yet); Step 2 note `done`,
  Step 4 note `running`; stale "finish OlympiadBench/GPQA" actions removed. Mrunmay's ARC envs + HF login are set up;
  verification (`check_envs`, activation test) still to run.

- **2026-10-10**: Team decision: all three teammates race each training run from their own ARC accounts and keep the
  first copy that finishes training (rules in the [decision log](reference/decision-log.md)). Mrunmay is setting up
  their account (Step 0), then submitting `random_s1`/`random_s2` (Step 3).

- **2026-10-10**: Disk plan. `/home` 522.4 / 640 GB (~118 GB free; Manas can't free much). Per training run: final model
  ~6.2 GB, ZeRO-3 checkpoint ~43–50 GB, **peak ~90–100 GB** (save_total_limit 1 keeps two briefly). One run at a time
  barely fits; two concurrent runs (~200 GB) don't. Two teammates with more quota are joining; options: train from their
  accounts/space, use /scratch, or `save_only_model: true` (peak ~15 GB, no exact resume). Undecided.

- **2026-10-10**: Base OlympiadBench done on 1× H200 (job 7921791): Acc 0.492 (ref 0.495), Pass@1 0.277; all 8 base benchmarks in.
  Step 4 launched (k=4). Sanity check on shard 0 chunk 0 (2000 prompts): median 750 gen tokens, p90 1314, 1.8% hit the
  8K cap, 1.8% empty answers. Healthy. ~1.1 A100-h per shard, ~18 A100 GPU-h total (above the 5–12 estimate).

- **2026-10-09**: Step 4 ready to launch with k=4 attempts per prompt (decision log), ~5–12 A100 GPU-h. Scoring script
  gets 32 GiB vLLM swap to avoid the OlympiadBench-style crash. Launch: `git pull && launch/score_pool.sh`.

- **2026-10-09**: Base OlympiadBench rerun on 2× A100 interactive (job 7921685, est. start Oct 11). A second copy races it on
  H200 via the new `OUT_TAG=h200` launcher option (writes to `eval/outputs/base_h200/`). Whichever finishes first is kept;
  cancel the other, and if H200 wins move its files into `eval/outputs/base/`.

- **2026-10-09**: Base GPQA done interactively (Acc 0.707, Pass@1 0.289; within gate tolerance). OlympiadBench crashed at
  600/675: `RuntimeError: Aborted due to the lack of CPU swap space` (vLLM default swap_space 4 GiB; `eval.py` has
  `swap_space=60` commented out). eval/ stays frozen; proposed fix: run on 2 GPUs (tensor parallel 2 = 2x KV cache, 8 GiB swap).
  Post-SFT evals (long traces) will hit this harder, so plan them on 2 GPUs or H200.

- **2026-10-08**: Added `analysis/explore_pool_audit.ipynb`, interactive Plotly views of `pool_audit.parquet` (sources,
  length vs cutoff, math selection funnel, answer kinds, duplicates, contamination, trace quality, slice explorer).
  Run it in a pandas 2.x env (anaconda `base` on Mac); pandas 3.0 + pyarrow 25 fails on `read_parquet`.

- **2026-10-08**: Base eval 6/8 done (see [Step 2](steps/02-base-eval.md#results)). Gate prints FAIL only because
  OlympiadBench/GPQA are missing and Minerva is 0.151 *above* ref; the eval env looks sound. Proposed a one-sided gate (Manas to decide).

- **2026-10-05**: Deadline is **Oct 20** (confirmed by Manas). A100 batch queue estimates Oct 10 for 1-GPU jobs;
  the remaining base-eval benchmarks run interactively (`LOCAL=1 launch/eval_model.sh base`).
- **2026-10-05**: Base eval moved from H200 (4-day queue) to A100. AIME done. Found that the leaderboard numbers are
  **pass@8**, so the gate now compares Acc; both metrics are reported. See the decision log.
- **2026-10-05**: Step 1 done. The pool is 67% math / 33% code and already clean apart from 3.7% truncation;
  91 verbatim test-set matches (AMC 4/40). Step 4 unblocked.
- **2026-10-05**: Step 1 audit job 7864578 failed at start: it ran in the old `vrr` env because `~/.bashrc` exports
  `CONDA_ENV`. Fixed (launchers use `SFT_ENV`, and an env sentinel runs in every job). Resubmit after `git pull`.
- **2026-10-05**: Docs reorganised into an Obsidian vault (`docs/`). Setup finished on ARC. Solved along the way:
  base-conda leakage into jobs, the torch/flash-attn pin, the transformers pin, the antlr4 conflict, and ARC's `$WORK`
  variable. See [Decision log](reference/decision-log.md) and [ARC guide](reference/arc-guide.md).
- **2026-10-05**: Repo created and pushed to `github.com/Manas-Ganti/acereasoning-sft100k`. SLURM account `tml_2026`.
