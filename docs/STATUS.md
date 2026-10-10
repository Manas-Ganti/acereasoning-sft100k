---
title: STATUS
current_step: 1
phase: setup done, starting Step 1
last_updated: 2026-10-08
updated_by: Manas + Claude
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
Step 1 audit done. Step 2: 6 of 8 base-eval benchmarks done (batch jobs 7865700–05). OlympiadBench and GPQA
(7865706–07) have not finished.

**Base model (Qwen2.5-3B-Instruct), as of 2026-10-08:**

| benchmark | Pass@1 | Acc (pass@8) | last year (pass@8) | gate |
|---|---|---|---|---|
| aime | 0.067 | 0.167 | 0.200 | ok |
| math | 0.646 | 0.854 | 0.844 | ok |
| cn_math_2024 | 0.133 | 0.400 | 0.233 | ok |
| kaoyan | 0.220 | 0.528 | 0.513 | ok |
| amc | 0.412 | 0.650 | 0.700 | ok |
| minerva | 0.303 | 0.489 | 0.338 | OFF (+0.151, *above* ref) |
| olympiadbench | — | — | 0.495 | crashed (vLLM CPU swap), rerun on 2 GPUs |
| gpqa | 0.289 | 0.707 | 0.742 | ok (−0.035, tol ±0.093) |

> [!NOTE]
> The gate prints FAIL only because two benchmarks are missing (LB avg = `nan`) and Minerva is *above* the reference.
> The eval environment looks sound: logs are clean and MATH matches within 0.01. Manas: matching last year's base is
> not required. A one-sided gate is proposed but not adopted yet. Details: [Step 2](steps/02-base-eval.md#results).

**Resume here:**
1. Finish OlympiadBench and GPQA: check `squeue -u $USER`; if still queued, run
   `BENCHES="olympiadbench gpqa" LOCAL=1 launch/eval_model.sh base` in an interactive A100 session
   (`srun -A tml_2026 -p a100_normal_q --qos=tc_a100_normal_int --gres=gpu:a100:1 -c 8 --mem=64G -t 2:00:00 --pty bash`, inside tmux).
2. Rerun `scripts/collect_results.py --gate base`; decide on the one-sided gate.
3. Submit Step 4 (`launch/score_pool.sh`).
4. Decide the training GPU plan (8 vs 4 GPUs per run) from `sinfo`/`sshare`/Owl/Falcon availability.

## Step board

| # | Step | Status | Gate / key result | Note |
|---|---|---|---|---|
| 0 | Setup | ✅ done | `check_envs` + batch activation test pass | [00-setup](steps/00-setup.md) |
| 1 | Audit pool | ✅ done | 67% math / 33% code; 3.7% truncated; 91 contaminated rows (AMC 4/40) | [01-audit-pool](steps/01-audit-pool.md) |
| 2 | Base eval + gate | 🔄 running (6/8 done) | 6/8 done; all within tolerance except Minerva, which is *above* ref; OlympiadBench + GPQA pending | [02-base-eval](steps/02-base-eval.md) |
| 3 | Random ×2 | ⬜ not started | seed spread = the bar | [03-random-baselines](steps/03-random-baselines.md) |
| 4 | Score pool | ⏭️ next (unblocked) | — | [04-score-pool](steps/04-score-pool.md) |
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
| 7865706–07 | base eval olympiadbench, gpqa | 2026-10-05 | not finished as of 2026-10-08 | — |
| 7927684_[0-15] | Step 4 score-gen, k=4, 16 × 1 A100 | 2026-10-09 | shards 0–1 done (~1.1 h each → ~18 A100 GPU-h total) | `work/scores/gen/` |
| 7927689 | Step 4 score-grade (CPU, afterok on 7927684) | 2026-10-09 | after all shards | — |
| 7927690 | Step 4 embed + k-means (1 A100) | 2026-10-09 | queued | `analysis/clusters_spotcheck.md` |

## Next actions

- [x] Step 1: audit, see [results](steps/01-audit-pool.md#results)
- [ ] Spot-check near-miss contamination (contam_score 0.3–0.5) before Step 5
- [ ] Step 2: finish OlympiadBench + GPQA (`LOCAL=1`), then `scripts/collect_results.py --gate base` (Acc vs last year)
- [ ] Step 4: after the audit finishes, `launch/score_pool.sh`
- [ ] Check `quota` before any training: each run peaks at about 100 GB of checkpoints

## Blockers / open questions

- **GPU scarcity:** on 2026-10-05, 1-GPU A100 batch jobs were estimated 4–5 days out, and H200 was worse. 8-GPU training
  may not schedule in time. Options: 4 GPUs with grad-accum 16 (same global batch 64; GA is a README "tweak" field),
  or Owl B200 / Falcon. Undecided: needs `sinfo`/`sshare` numbers and Manas's decision.
- Disk: `/home` had ~151 GB free before two old repos were deleted, and the quota display updates later. Re-check
  `quota` before Step 3.

## Change log (newest first)

- **2026-10-10**: Base OlympiadBench done on 2 GPUs: Acc 0.492 (ref 0.495), Pass@1 0.277; all 8 base benchmarks in.
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
