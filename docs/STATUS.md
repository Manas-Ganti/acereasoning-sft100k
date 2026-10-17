---
title: STATUS
current_step: 6
phase: Steps 3 + 6 training queued (random_s1/s2, full_method_s1); Step 7 prep
last_updated: 2026-10-13
updated_by: Sahasree + Claude
tags: [status]
---

# STATUS: where the project is

> [!IMPORTANT]
> **Read this first, update it last.** Anyone, human or agent, who submits a job, gets a result, makes a decision or
> hits a blocker updates this file before stopping. Keep it short and current, and move detail into the step notes.
> Protocol: [CLAUDE.md, "Start here"](../CLAUDE.md).

## Now

> [!IMPORTANT]
> **Eval status and GPU queue (Mrunmay, 2026-10-15 17:30).** Three eval blockers were found and fixed (tokenizer +
> chat template, spawn, swap), and random_s1 has real scores on 3/8 benchmarks. The Tinkercliffs A100 queue is full:
> `sbatch --test-only` for every new A100 shape tried (1 or 2 GPUs, 1.5–8 h, short or interactive QOS) gave
> **Oct 24**. Mrunmay's waiting interactive request 8003894 (2 GPUs, 4 h) is estimated for Oct 18 15:49. Eval
> progress:
>
> | model | test benchmarks with scores | still to run |
> |---|---|---|
> | random_s1 | aime, amc, cn_math_2024 | math, kaoyan, minerva, olympiadbench, gpqa (batch 7999723/25/27/28/29, queued) |
> | random_s2 | none | all 8: aime/amc/cn_math/kaoyan resubmitted after crashing (8004201–04); math/minerva/olympiad/gpqa queued (7934180/84/85/86) |
> | full_method_s1 | none | all 8 (Manas) |

> [!NOTE]
> **Eval failures found on 2026-10-15 and their fixes** (details in the [decision log](reference/decision-log.md)).
> All three hit trained models only, and SLURM still reports the job as **COMPLETED**, because `eval_single.sh`
> pipes through `tee`. A trained-model eval that "finished" in a few minutes, or whose log has no `Acc:` line, crashed.
>
> | failure | cause | fix (on each ARC account / model) |
> |---|---|---|
> | `untagged enum ModelWrapper` at tokenizer load | myenv writes a `tokenizer.json` that evalenv's transformers 4.44.2 can't parse | `scripts/fix_tokenizer_for_eval.py <run>` (also copies `chat_template.jinja` into `tokenizer_config.json` since `ed20bc5`); `train.slurm` runs it for jobs submitted after `64219e1` |
> | `Cannot re-initialize CUDA in forked subprocess`, or `DistStoreError ... 1/2 clients joined` | 2-GPU vLLM forks a worker after `eval.py` has initialised CUDA | `env/vllm_spawn_hook.sh`, once per account (applies to queued jobs too) |
> | `Aborted due to the lack of CPU swap space` | long traces overflow vLLM's 4 GiB/GPU swap default | `env/vllm_swap_hook.sh`, once per account (applies to queued jobs too) |
>
> Status: both hooks are installed on mrunmayp and manasganti. The tokenizer fix has been applied to random_s1 and
> random_s2. The random_s2 smoke test (`scripts/smoke_eval.py`) passed on 2× A100 with these fixes.

> [!NOTE]
> **Queue observations (2026-10-15):** `sbatch --test-only` gave a new 2× H200 8 h job **Nov 8**, and new A100 jobs
> Oct 24. The 4 h interactive QOS (`tc_a100_normal_int`) allocated within minutes at ~13:50, but at 17:30 its estimate
> was Oct 18.

Setup is complete on ARC: both envs are built and verified, the pool and base model are downloaded, and the dev set
is built. Activation inside batch jobs was verified with `launch/test_activation.sh`, which passed for both envs.
Step 1 audit done. Step 2: all 8 base-eval benchmarks done (OlympiadBench on 1× H200, job 7921791). Steps 4 and 5 done (2026-10-12).
**Step 3 (2026-10-15):** `random_s1` and `random_s2` are **trained** (7 h 44 min / 5 h 28 min, 8× A100-80GB) and
tokenizer-fixed. **No eval results yet.** random_s1's evals were resubmitted (7999722–29), and random_s2's are
queued (7934179–87).

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

**Resume here (updated 2026-10-15 by Mrunmay + Claude):**
0. ✅ **Smoke test `random_s2` PASSED (Mrunmay, 2026-10-15 14:09, 2× A100 interactive, tc-gpu003)**, with the tokenizer +
   chat-template fix and the vLLM spawn hook: vLLM loaded with TP=2 in 57 s; 4/4 samples `finish=stop` (368–1901
   tokens) and 4/4 have `\boxed{}`. random_s1 aime/amc/cn_math then ran in that session (`LOCAL=1`); their batch
   copies 7999722/24/26 were cancelled.
1. **`full_method_s1`** (Manas's account): see its [run note](runs/full_method_s1.md).
2. **`longest_s1`:** see its [run note](runs/longest_s1.md). Jobs submitted before `64219e1` don't run the tokenizer fix
   automatically.
3. **Step 3 (Mrunmay):** random_s1 evals 7999723/25/27/28/29 and random_s2 evals 7934180/84/85/86 are queued (with
   both hooks). random_s2 aime/amc/cn_math/kaoyan resubmitted as 8004201–04; interactive request 8003894 is also waiting (est. Oct 18).
   Dev evals 7934177 / 7934187 are lowered in priority (`nice=500`).
4. **Ablations are not trained** (decision log 2026-10-12: focus on required parts). Only if GPUs free up late: submit **`filter_only_s1`** (the high-value ablation: "is the gain just
   from dropping code + cleaning?"). On your account:
   `git pull && ~/.conda/envs/evalenv/bin/python scripts/subset_from_idx.py filter_only_s1 && DRY_RUN=1 EVAL=1 launch/train.sh filter_only_s1`,
   check the preview, then submit without `DRY_RUN`. Push the job IDs here and create `docs/runs/filter_only_s1.md`.
5. **`filter_difficulty_s1`: skipped** (decided). Its data barely differs from `filter_only` (78% of
   filter_only is already in the difficulty band), so the effect would likely be within noise. Submit it only if GPUs are free.
   The subset is built and committed either way.
6. **Step 6 (Manas):** `full_method_s1` submitted 2026-10-12 (train 7958393, evals 7958394–401, dev 7958402).
7. **Second smart method `longest_s1` (new 2026-10-13, approved by Manas):** script `scripts/select_longest.py`
   is ready. The account holding `analysis/pool_scores.parquet` builds it, commits the idx + meta and submits it
   (steps in the [run note](runs/longest_s1.md)). The kept smart model is chosen on the **dev set** (decision log 2026-10-13).
8. When runs finish: `scripts/collect_results.py`, fill in the run notes, push `results/` + logs.
9. Manas: decide on the one-sided Step 2 gate (not blocking).

## Step board

| # | Step | Status | Gate / key result | Note |
|---|---|---|---|---|
| 0 | Setup | ✅ done | `check_envs` + batch activation test pass | [00-setup](steps/00-setup.md) |
| 1 | Audit pool | ✅ done | 67% math / 33% code; 3.7% truncated; 91 contaminated rows (AMC 4/40) | [01-audit-pool](steps/01-audit-pool.md) |
| 2 | Base eval + gate | ✅ eval done (gate decision open) | all 8 in; LB6 pass@8 0.544 vs 0.503; FAIL only from scores *above* ref (Minerva, CN Math) | [02-base-eval](steps/02-base-eval.md) |
| 3 | Random ×2 | 🔄 queued (7934168 / 7934178) | seed spread = the bar | [03-random-baselines](steps/03-random-baselines.md) |
| 4 | Score pool | ✅ done | pass_rate median 0 / mean 0.26 (k=4); r1_agreement median 0.5; 100 clusters (181–1242) look like topics; ~20.5 A100 GPU-h | [04-score-pool](steps/04-score-pool.md) |
| 5 | Selection | ✅ done | 3 subsets × 15,000 (seed 1); difficulty band leaves 41,626 unique prompts; full_method uniform over 100 clusters | — | [05-selection](steps/05-selection.md) |
| 6 | Smart model (ablations skipped) | 🔄 `full_method_s1` queued (7958393); `longest_s1` script ready, not built; ablations not trained (decision log) | — | [06-ablations](steps/06-ablations.md) |
| 7 | Compare + submit | ⬜ not started | deadline **Oct 20** | [07-compare-submit](steps/07-compare-submit.md) |

Legend: ⬜ not started · ⏭️ next · 🔄 running · ✅ done · ⛔ blocked / gate failed

## Running jobs

| Job ID | What | Submitted | Expected | Log |
|---|---|---|---|---|
| 7865518–25 | base eval on H200 | 2026-10-05 | cancelled (4-day queue) | — |
| (AIME) | base eval aime, A100 | 2026-10-05 | ✅ done: Pass@1 0.067, Acc 0.167 | `eval/outputs/base/log_aime.txt` |
| 7865701–05 | base eval math, cn_math, kaoyan, amc, minerva | 2026-10-05 | ✅ done | `logs/slurm/eval-base-*.out` |
| 7865706–07 | base eval olympiadbench, gpqa | 2026-10-05 | superseded: GPQA done interactively, OlympiadBench by 7921791 (1× H200) | — |
| 7927684_[0-15] | Step 4 score-gen, k=4, 16 × 1 A100 | 2026-10-09 | ✅ done (~20.5 A100 GPU-h) | `work/scores/gen/` |
| 7927689 | Step 4 score-grade (CPU, afterok on 7927684) | 2026-10-09 | ✅ done | — |
| 7927690 | Step 4 embed + k-means (1 A100) | 2026-10-09 | ✅ done | `analysis/clusters_spotcheck.md` |
| 7934168 | Step 3 train `random_s1`, 8× A100 (mrunmayp) | 2026-10-10 | ✅ done Oct 13, 7 h 44 min | `LLaMA-Factory/saves/qwen25_3b_instruct/random_s1/train.log` |
| 7934169–77 | `random_s1` 8 evals (2× A100 each) + dev eval, afterok 7934168 | 2026-10-10 | ❌ 8 evals crashed (tokenizer; outputs in `eval/outputs/random_s1_crashed_tokenizer/`); dev 7934177 pending, est. Oct 19 |
| 7999722–29 | `random_s1` 8 evals **resubmitted** after tokenizer fix (aime, math, cn_math, kaoyan, amc, minerva, olympiadbench, gpqa) | 2026-10-15 | pending, start N/A | [run note](runs/random_s1.md) |
| 7934178 | Step 3 train `random_s2`, 8× A100 (mrunmayp) | 2026-10-10 | ✅ done Oct 14, 5 h 28 min | `LLaMA-Factory/saves/qwen25_3b_instruct/random_s2/train.log` |
| 7934179–87 | `random_s2` 8 evals (2× A100 each) + dev eval, afterok 7934178 | 2026-10-10 | tokenizer fixed; aime est. Oct 15 21:54, others Oct 19 03:25 or N/A | [run note](runs/random_s2.md) |
| 8004201–04 | `random_s2` aime, amc, cn_math_2024, kaoyan **resubmitted** (first copies crashed: fork ×3, swap ×1) | 2026-10-15 | queued |
| 7958393 | Step 6 train `full_method_s1`, 8× A100 (manasganti) | 2026-10-12 | est. start Oct 15 18:29 (tc-gpu003); ≤23 h | `LLaMA-Factory/saves/qwen25_3b_instruct/full_method_s1/` |
| 7958394–7958402 | `full_method_s1` 8 evals (2× A100 each) + dev eval, afterok 7958393 | 2026-10-12 | **on hold (JobHeldUser)** until tokenizer fix + smoke test pass, then `scontrol release` | [run note](runs/full_method_s1.md) |

## Next actions

- [x] Step 1: audit, see [results](steps/01-audit-pool.md#results)
- [x] Step 2: all 8 base benchmarks done (one-sided gate decision still open)
- [x] Step 3: `random_s1`/`random_s2` generated and submitted (Mrunmay)
- [x] Step 4: scoring, grading and clustering done, see [results](steps/04-score-pool.md#results)
- [x] Step 5: `filter_only_s1`, `filter_difficulty_s1`, `full_method_s1` built and committed, see [results](steps/05-selection.md#results)
- [x] Step 6: `full_method_s1` submitted (Manas, 7958393)
- [x] Step 6: ablations not trained (decision log 2026-10-12); `filter_only_s1` only if GPUs free up late
- [ ] Step 6: build + submit `longest_s1` ([run note](runs/longest_s1.md); needs `pool_scores.parquet`)
- [ ] Spot-check near-miss contamination (contam_score 0.3–0.5): optional, report as a limitation if skipped
- [ ] Step 7: results table, report, HF uploads (deadline **Oct 20**)

## Blockers / open questions

- **Disk for training (updated 2026-10-12):** Manas's account holds `full_method_s1` (~118 GB free, one run).
  Mrunmay's holds `random_s1` + `random_s2`. `filter_only_s1` needs a third account or space freed after a run finishes.
  Earlier note (2026-10-10): Mrunmay's `/home` has a 640 GB quota and is nearly empty (only setup files),
  enough for `random_s1` + `random_s2` at once (~200 GB peak). Still open for runs on Manas's account:
  ~118 GB free on Manas's `/home` vs ~100 GB peak per run. Decide where training
  runs live (teammates' quota / scratch / `save_only_model`). Two teammates are joining the project.

- **GPU scarcity:** on 2026-10-05, 1-GPU A100 batch jobs were estimated 4–5 days out, and H200 was worse. 8-GPU training
  may not schedule in time. Options: 4 GPUs with grad-accum 16 (same global batch 64; GA is a README "tweak" field),
  or Owl B200 / Falcon. Undecided: needs `sinfo`/`sshare` numbers and Manas's decision.
- Disk: `/home` had ~151 GB free before two old repos were deleted, and the quota display updates later. Re-check
  `quota` before Step 3.

## Change log (newest first)

- **2026-10-17**: Launchers accept `GPU=l40s|a30` (Falcon) for evals; see the decision log. Untested: validate with a
  base AIME run on 2× L40S before trusting it.

- **2026-10-15 17:30**: A100 queue full: every new A100 shape is estimated for Oct 24; interactive 8003894 for Oct 18.
  random_s2: 0/8 benchmarks scored. Top of Now rewritten as status only: eval progress table, failure/fix table,
  queue observations.

- **2026-10-15**: Manas's account: vLLM spawn + swap hooks installed in evalenv (swap default 24 GiB/GPU);
  `check_envs.sh` ALL CHECKS PASSED. `full_method_s1` evals (held) will start with both hooks.

- **2026-10-15**: random_s2 batch evals aime/amc/cn_math (started 12:17–13:51, before the spawn hook) died with
  `DistStoreError ... 1/2 clients joined` (forked worker crash); kaoyan (14:18, after the spawn hook) died on CPU swap.
  random_s1 gpqa (interactive) also died on swap at 94/198. Swap hook installed 16:38 on mrunmayp (`env/vllm_swap_hook.sh`).
  All five reruns pending; crashed logs moved to `eval/outputs/random_s{1,2}_crashed*/`. Batch evals still queued now get
  both hooks at start. random_s2 short benchmarks + kaoyan to run in a new interactive session.

- **2026-10-15**: Smoke test `random_s2` PASS on 2× A100 (TP=2, spawn hook): loads in 57 s; 4/4 samples stop with a
  `\boxed{}` answer. The 2-GPU fork crash (`Cannot re-initialize CUDA in forked subprocess`) is fixed by
  `env/vllm_spawn_hook.sh` (run once per account). random_s1 short benchmarks are running interactively.

- **2026-10-15**: `smoke_eval.py` gains login-node file checks (`--static-only`, no GPU, seconds): config.json fields
  vs base, `torch_dtype` = bfloat16 (vLLM 0.6.1 would otherwise fall back to fp16), generation_config eos incl. 151645,
  tokenizer eos `<|im_end|>`, chat template present. Tested against the base model's files (passes). Tip from another
  agent: on ARC, `ib0` has no IPv4 on A100 nodes too. If a 2-GPU smoke test dies in NCCL init, resubmit evals with
  `NCCL_SOCKET_IFNAME=eth0` exported.

- **2026-10-15**: `full_method_s1` training 7958393 est. start Oct 15 18:29 (tc-gpu003). Its 9 eval/dev jobs are held
  (`scontrol hold`) so they can't start before the tokenizer fix (the job predates `64219e1`). Training job untouched.

- **2026-10-15**: New `scripts/smoke_eval.py <run>`: a ~10-min check that a trained model works in evalenv exactly as
  eval.py uses it (tokenizer + chat template with the eval system prompt, vLLM load with tensor parallel = visible GPUs,
  generation stops at EOS, answers contain `\boxed{}`). No trained model has completed an eval yet, so run it once on
  `random_s2` (already trained + fixed) in a 2-GPU interactive session before the real evals start.

- **2026-10-15**: Second eval blocker found before it hit: myenv saves the chat template only to `chat_template.jinja`,
  which eval's transformers 4.44.2 ignores. `fix_tokenizer_for_eval.py` (ed20bc5) copies it into
  `tokenizer_config.json`; applied to random_s1 and random_s2 (both "ok"). Training curves healthy (s1 loss 0.99 → 0.56).

- **2026-10-15**: Team alert added at the top of Now: run the tokenizer fix on every trained model before its evals start;
  evals "COMPLETED" in under a few minutes have crashed. A100 eval queue estimates reach Oct 19; check H200 with
  `sbatch --test-only` before adding jobs. Resume list rewritten per person.

- **2026-10-15**: Eval crash diagnosed: myenv saves a `tokenizer.json` that evalenv (transformers 4.44.2) cannot parse
  ("untagged enum ModelWrapper"). **Affects every trained model** (random_s1/s2, full_method_s1, longest_s1). Fix:
  `~/.conda/envs/evalenv/bin/python scripts/fix_tokenizer_for_eval.py <run>` on each trained model before its evals
  start (decision log). `train.slurm` now does it automatically for newly submitted jobs only.

- **2026-10-15**: `random_s1` trained (7 h 44 min) and `random_s2` trained (5 h 28 min), both 8× A100-80GB, 5.8 GB each.
  **All 8 `random_s1` test evals ended "COMPLETED" in 19–66 s: almost certainly crashed** (`tee` hides the exit code).
  Logs being checked before anything is resubmitted; the same failure may hit `random_s2` and `full_method_s1` evals.

- **2026-10-13**: Second smart method approved by Manas: `longest_s1` = `full_method`'s quality filter + R1-majority rule,
  then the 15,000 longest traces (`scripts/select_longest.py`, new; existing scripts unchanged; logic checked on
  synthetic data). The smart model is picked on the dev set, by a rule fixed in advance (decision log). Not built or submitted
  yet: needs `pool_scores.parquet`. Expect more training tokens than random, so a longer run.

- **2026-10-13**: `random_s1` / `random_s2` (7934168 / 7934178) still PENDING (Priority); both start estimates passed.
  Stale Step 4 rows in Running jobs marked done.

- **2026-10-12**: Report draft started: `report/report.md` (setup, base results, pool findings, selection method +
  funnel, experiments, findings, limitations, reproducibility). Results and abstract are TODO until the evals land.

- **2026-10-12**: Decided to focus on required parts: train random_s1, random_s2 and full_method_s1 only; ablations built
  but not trained. Next while training queues: Step 7 prep (report draft, README, HF dataset uploads).

- **2026-10-12**: Plan for the remaining ablations: `filter_only_s1` high value (submit from a teammate's account);
  `filter_difficulty_s1` proposed to skip unless GPUs are free (small expected effect). Step board, resume list and next
  actions brought up to date.

- **2026-10-12**: Step 6: `full_method_s1` submitted from Manas's account: train 7958393 (8× A100), evals 7958394–401
  (2× A100 each), dev 7958402. `filter_only_s1` / `filter_difficulty_s1` still to submit (teammate with ~220 GB free).

- **2026-10-12**: Step 5 done: `filter_only_s1`, `filter_difficulty_s1`, `full_method_s1` built on Manas's account (funnels in
  the Step 5 note). R1-agreement spot-check: math-only mean 0.917 / median 1.0; disagreements are about half genuine,
  half notation; filter kept. Next: Step 6 training (3 runs × 8 A100; ~100 GB peak disk each).

- **2026-10-12**: Step 4 done: all 16 score-gen shards, score-grade (7927689, 1h35) and embed (7927690, 4.5 min)
  COMPLETED. pass_rate median 0, mean 0.26 over 67,432 math rows; r1_agreement median 0.5 (28,372 rows; spot-check
  pending); clusters are clean topics. Step 5 unblocked: band stays [0, 0.5] (decision log). New `scripts/subset_from_idx.py`
  lets teammates rebuild subsets without `pool_scores.parquet`.

- **2026-10-12**: Step 3 still pending (Priority). Start estimates slipped: `random_s1` 7934168 → Oct 12 22:23 (tc-gpu001),
  `random_s2` 7934178 → Oct 13 02:51 (tc-gpu004). Step 4 jobs 7927684/89/90 no longer in `squeue`; outcome unknown
  (outputs are on Manas's account, nothing committed).

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
