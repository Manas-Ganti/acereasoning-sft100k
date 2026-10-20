---
title: "Selecting 15K Reasoning Examples for SFT: Difficulty- and Topic-Aware Selection vs Random"
course: ECE 6514 (Trustworthy ML), Fall 2026
status: final draft
last_updated: 2026-10-20
---

# Selecting 15K Reasoning Examples for SFT: Difficulty- and Topic-Aware Selection vs Random

> [!NOTE]
> Every number here comes from the repo: the eval logs in `eval/outputs/<run>/log_<bench>.txt`, `docs/runs/*.md`,
> `docs/steps/*`, `docs/reference/decision-log.md` and `data_subsets/*.meta.json`.

**Team:** Manas Ganti, Mrunmay Paratwar, Sahasree Datla

**Code:** https://github.com/Manas-Ganti/acereasoning-sft100k

**Datasets:** random 15K https://huggingface.co/datasets/Mrunmayp/acereason-random15k · smart 15K
https://huggingface.co/datasets/Mrunmayp/acereason-smart15k

**Models:** random-subset https://huggingface.co/Mrunmayp/qwen25-3b-acereason-random15k · smart-subset 

## Abstract

We pick 15,000 of the 100,000 DeepSeek-R1-distilled reasoning traces in AceReason-1.1-SFT to fully fine-tune
Qwen2.5-3B-Instruct, and ask whether a deliberate choice beats a random one by more than seed noise. Our method keeps
clean math only (no code, no traces cut by the 16K training cutoff, no proofs, no test overlap), keeps problems the
base model solves at most half the time (from 4 sampled attempts graded against R1's answer, with a label-noise
filter), and balances 100 topic clusters. We train two random baselines (seeds 1, 2) and the smart subset at identical
hyperparameters and evaluate all on the course's eight benchmarks. **The smart subset does not beat random by more than
noise.** On the six leaderboard benchmarks, its Pass@1 is 0.263 against 0.255 / 0.261 for the random seeds (gap to the
random mean +0.005, seed spread 0.006), and its pass@8 is 0.575 against 0.561 / 0.566 (+0.009, spread 0.005, but below
the ≈1-point hardware and grader noise we measured). All three fine-tuned models score *below* the base model on
Pass@1 (0.272) and *above* it on pass@8 (0.544). The pool turned out to be very hard for a 3B model (median base
pass rate 0), so the difficulty band is dominated by problems the model never solves.

---

## 1. Task and setup

**Question.** Does a deliberately chosen 15K subset of a 100K reasoning pool fine-tune a small model better than a
random 15K subset, at identical hyperparameters, by more than seed-to-seed noise?

| Component | Setting |
|---|---|
| Base model | `Qwen/Qwen2.5-3B-Instruct` |
| Pool | `redsgnaoh/acereason11_100k`: 100,000 examples from NVIDIA AceReason-1.1-SFT. Every response is distilled from DeepSeek-R1 (`<think>…</think>` + final solution). 67,432 math, 32,568 code |
| Subset size | exactly 15,000 examples per run |
| Training | LLaMA-Factory (course snapshot), the course README YAML verbatim: full fine-tune, DeepSpeed ZeRO-3 offload, FlashAttention-2, lr 5e-6, 3 epochs, per-device batch 1 × grad-accum 8 × 8 GPUs = **global batch 64**, cosine schedule, no warmup, `cutoff_len` 16384, `qwen` template, bf16. ≈703 optimizer steps per run |
| Hardware | VT ARC Tinkercliffs, 8× A100 per training run |
| Evaluation | The course `eval/` folder, unmodified (checksums verified): vLLM sampling at temperature 0.6, top-p 0.95, **8 samples per question**, max 32,768 tokens; SymPy `\boxed{}` grader |
| Benchmarks | AIME24 (30), MATH-500 (499), CN-Math-2024 (30), Kaoyan (199, Chinese, mostly multiple choice), AMC23 (40), Minerva (272), OlympiadBench (675), GPQA-Diamond (198, multiple choice) |
| Metrics | **Pass@1** (mean accuracy over the 8 samples), our primary metric because it's less noisy. **Acc = pass@8** (≥1 of 8 correct), the course leaderboard metric. **avg(LB6)** = mean over the six leaderboard benchmarks available locally (CN-Math, Kaoyan, AMC, Minerva, OlympiadBench, GPQA; the leaderboard's AIME25 isn't in `eval/data`) |

**Comparison rule.** Runs differ **only in their training data**: same base model, YAML, template, cutoff, GPU
count and eval. A gap between the smart subset and random counts as an improvement only if it is larger than the gap
between the two random seeds.

**System prompt (deliberate, identical for every run).** Datasets are registered exactly as the course README
does (`{"<name>": {"file_name": "<name>.json"}}`), so training uses the Qwen template's default system prompt, while
eval uses "Please reason step by step, and put your final answer within \boxed{}." Because it's the same for every
run, it doesn't bias the comparison.

## 2. Base model

The untrained Qwen2.5-3B-Instruct, evaluated with the unmodified eval (1 GPU per benchmark; OlympiadBench on 1× H200,
see §8):

| | AIME24 | MATH | CN-Math | Kaoyan | AMC | Minerva | OlympiadBench | GPQA | avg(LB6) |
|---|---|---|---|---|---|---|---|---|---|
| Pass@1 | 0.067 | 0.646 | 0.133 | 0.220 | 0.412 | 0.303 | 0.277 | 0.289 | 0.272 |
| Acc (pass@8) | 0.167 | 0.854 | 0.400 | 0.528 | 0.650 | 0.489 | 0.492 | 0.707 | 0.544 |
| Last year's baseline (Acc) | 0.200 | 0.844 | 0.233 | 0.513 | 0.700 | 0.338 | 0.495 | 0.742 | 0.503 |

Our numbers match last year's within a problem or two everywhere except Minerva (+0.151) and CN-Math (+0.167 =
5 of 30 problems), where we score *higher*. A broken eval would lower scores, and the hardest-to-grade
benchmarks (MATH, OlympiadBench) agree within 0.01, so we take the eval environment as sound.

## 3. The pool: what we found before selecting

We measured every one of the 100K examples (tokenizer: Qwen2.5; `scripts/audit_pool.py`):

| | Math | Code |
|---|---|---|
| Rows (unique prompts) | 67,432 (59,702) | 32,568 (24,391) |
| Response length, median / p90 (tokens) | 6,641 / 14,238 | 6,120 / 14,004 |
| Longer than the 16,384-token training cutoff | 3.7% | 2.8% |
| Final answer in a balanced `\boxed{}` | 99.3% | 0% (answers are code) |

Further findings:
- **Truncation teaches the wrong ending.** 3,452 examples exceed `cutoff_len`. Training cuts them before the final
  answer, which teaches the model to stop without one. A random 15K subset contains about 520 of them.
- **Contamination.** 91 pool rows contain a test question nearly verbatim (≥50% of its word 8-grams): AMC 4 of 40, MATH 19
  questions (54 rows), OlympiadBench 27 questions (33 rows). A further 81 rows overlap our dev set.
- **Duplicates.** 28,372 rows share their prompt with another row (up to 11 R1 responses per prompt).
- **Proof-style and prose answers.** 4,176 math rows (6.2%) ask for a proof or box a sentence. They can't be checked
  against an answer.
- **Quality flags** (repetition loops, language mixing, malformed think tags) are rare: 6 rows.

## 4. Selection method

The smart subset (`full_method_s1`) is built in four stages from per-example scores. Everything is deterministic
(seed 1) and implemented in `scripts/select_subset.py`.

### 4.1 Clean math only
Keep math examples that fit in 16,384 tokens, end with a balanced `\boxed{}` answer, aren't proof-like or prose,
don't overlap the test or dev sets, and carry no quality flag. **Why math only:** none of the eight benchmarks test
code, and code responses have no `\boxed{}` answer to learn the answer format from or to grade against.

### 4.2 Difficulty for *this* model
For each of the 59,702 unique math prompts, the base model generated **4 attempts** (same sampling as the eval, with a
cap of 8,192 tokens; capped attempts count as wrong). The frozen eval grader compared each attempt with **R1's boxed
answer**, used as a pseudo-label, giving a pass rate in {0, ¼, ½, ¾, 1}. Cost: ≈20.5 A100 GPU-hours over 16 parallel jobs.
- Keep pass rate **≤ 0.5** (problems the model solves at most half the time). Problems it already solves teach it little.
- **Label-noise check.** For prompts with several R1 responses, we grouped equivalent final answers. A never-solved row
  is dropped if its R1 answer is not the strict majority among R1's responses, because R1's label is then likely wrong.

### 4.3 Topic balance
We embedded each prompt (`BAAI/bge-base-en-v1.5`) and ran k-means with k=100. The clusters are recognisable topics:
functional equations, probability, triangle geometry, inequalities, conics, combinatorics on grids, and so on; sizes range
from 181 to 1,242 prompts. We sample with **max-min fair quotas** across clusters (water-filling): every cluster gets
the same share, capped by what it has.

### 4.4 One response per prompt
Where a prompt has several R1 responses, we keep one, preferring one that agrees with the R1 majority, so 15,000
rows = 15,000 distinct problems.

### 4.5 Funnel and resulting composition

| Step | Rows left |
|---|---|
| Pool | 100,000 |
| Math | 67,432 |
| Fits in 16,384 tokens | 64,907 |
| Balanced `\boxed{}` answer | 64,712 |
| Not proof-like / prose | 60,648 |
| Not in test set / dev set | 60,586 / 60,508 |
| No quality flag | 60,504 |
| Pass rate ≤ 0.5 | 47,768 |
| Drop never-solved rows with a minority R1 answer | 46,333 |
| One response per prompt | 41,626 unique problems |
| Topic-balanced sample | **15,000** |

| | Random (`random_s1`) | Smart (`full_method_s1`) |
|---|---|---|
| Math / code | 10,192 / 4,808 | 15,000 / 0 |
| Truncated at 16,384 | 520 | 0 |
| Overlap with test questions | 14 | 0 |
| Base pass rate 0 / ¼ / ½ (of math) | not computed (uniform over all pass rates) | 10,612 / 2,619 / 1,769 |
| Topic clusters | not balanced (uniform over the pool) | 100 × 150 rows (1.0% each) |
| Training tokens (capped at cutoff) | ≈112M | 112.3M |
| Median example length | 6,617 tokens | 6,802 tokens |

Both subsets have nearly the same number of training tokens, so compute isn't a confound. Fingerprints (sha256 of
the sorted pool indices): `random_s1` `6212267e…`, `random_s2` `b55e6eaa…`, `full_method_s1` `d733da24…`.

## 5. Experiments

| Run | Data | Purpose | Status |
|---|---|---|---|
| `random_s1` | uniform random 15K of 100K, seed 1 | baseline | trained 7 h 44 min (8× A100), loss 0.633; 8/8 evals (Minerva regraded, §6) |
| `random_s2` | uniform random 15K of 100K, seed 2 | second baseline → **seed spread** (noise floor) | trained 5 h 28 min (8× A100), loss 0.631; 8/8 evals |
| `full_method_s1` | §4, seed 1 | the smart subset | trained 20 h 04 min (8× A100, slower node), loss 0.569; 8/8 evals |

All three trained for 705 optimizer steps with the same YAML. Training losses aren't comparable across runs (different
data mixes). Wall-time differences come from the nodes, not the configs.

**Noise accounting.** The **seed spread** (max − min over the two random runs) covers data sampling plus training
nondeterminism, and is the bar a gap must clear. Two seeds give only a rough estimate of it, so we also report the
two measured sources of eval-side noise (§6.3). We didn't compute bootstrap CIs, because the per-sample outputs
stayed on the cluster accounts.

## 6. Results

Official `Acc` / `Pass@1` lines from each benchmark's eval log (`eval/outputs/<run>/log_<bench>.txt`), one
exception marked ‡. ★ = in the leaderboard average. avg(8) is over all eight benchmarks; avg(LB6) over the six ★.

### 6.1 Pass@1 (mean over 8 samples; primary metric)

| Model | AIME24 | MATH | ★CN-Math | ★Kaoyan | ★AMC | ★Minerva | ★Olympiad | ★GPQA | avg(8) | **avg(LB6)** |
|---|---|---|---|---|---|---|---|---|---|---|
| Base | 0.067 | 0.646 | 0.133 | 0.220 | 0.412 | 0.303 | 0.277 | 0.289 | 0.293 | **0.272** |
| random_s1 | 0.063 | 0.649 | 0.092 | 0.256 | 0.372 | 0.277‡ | 0.272 | 0.265 | 0.281 | **0.255** |
| random_s2 | 0.079 | 0.650 | 0.133 | 0.256 | 0.359 | 0.277 | 0.272 | 0.269 | 0.287 | **0.261** |
| full_method_s1 | 0.054 | 0.668 | 0.113 | 0.241 | 0.397 | 0.281 | 0.272 | 0.275 | 0.288 | **0.263** |

### 6.2 Acc = pass@8 (any of 8 samples correct; leaderboard metric)

| Model | AIME24 | MATH | ★CN-Math | ★Kaoyan | ★AMC | ★Minerva | ★Olympiad | ★GPQA | avg(8) | **avg(LB6)** |
|---|---|---|---|---|---|---|---|---|---|---|
| Base | 0.167 | 0.854 | 0.400 | 0.528 | 0.650 | 0.489 | 0.492 | 0.707 | 0.536 | **0.544** |
| random_s1 | 0.233 | 0.864 | 0.333 | 0.638 | 0.675 | 0.452‡ | 0.507 | 0.763 | 0.558 | **0.561** |
| random_s2 | 0.233 | 0.848 | 0.367 | 0.608 | 0.700 | 0.452 | 0.501 | 0.768 | 0.560 | **0.566** |
| full_method_s1 | 0.133 | 0.872 | 0.367 | 0.603 | 0.700 | 0.474 | 0.505 | 0.798 | 0.557 | **0.575** |

‡ **random_s1 Minerva is a regrade, not an official log line.** Its eval hung in grading on both attempts (jobs
7999727 and 8051762, TIMEOUT at 10 h and 4 h), after generation had finished and saved its outputs. Generation is
deterministic (both attempts wrote an identical 60,862,951-byte completions file). We regraded that file on CPU
with the eval's own, unmodified parsing and grading functions (`scripts/diagnose_grading_hang.py`, nothing under
`eval/` touched); no sample hung. The result happens to equal random_s2's official Minerva score exactly
(0.4522 / 0.2767). That is a coincidence: the two models' responses differ.

**Hardware.** Base and both random models were evaluated on Tinkercliffs A100s (base on 1 GPU, OlympiadBench on
1× H200; trained models on 2× A100). `full_method_s1` was evaluated on Falcon 2× L40S, because that queue was free.
Sampling settings and code are identical.

### 6.3 Smart vs random, against noise

| | Pass@1 avg(LB6) | Acc avg(LB6) |
|---|---|---|
| random_s1 / random_s2 | 0.255 / 0.261 | 0.561 / 0.566 |
| **Seed spread** (the bar) | **0.006** | **0.005** |
| full_method_s1 | 0.263 | 0.575 |
| Gap to random mean | +0.005 | +0.009 |
| Gap to the better random seed | +0.002 | +0.009 |
| Verdict | **within seed spread** | above the 2-seed spread, **below eval noise** |

Two measured eval-side noise sources are as large as these gaps:
- **Hardware.** `full_method_s1` MATH also ran on Tinkercliffs 2× A100: Pass@1 0.659 / Acc 0.854, against 0.668 / 0.872
  on L40S. That is the same model, data and sampling, differing by 0.009 Pass@1 and 0.018 Acc on a 499-problem benchmark.
- **Grader load.** Grading random_s2's Minerva again on a quieter machine flipped 5 responses (3 problems) from wrong
  to right: +0.011 Acc, +0.002 Pass@1 (§8).

With only two random seeds the spread itself is uncertain (last year's two random runs differed by 4 points of
pass@8). We therefore **do not claim an improvement**: the smart subset is indistinguishable from random on Pass@1,
and its +0.9-point pass@8 edge is smaller than the noise measured on a single benchmark.

Per benchmark (Pass@1), `full_method_s1` is highest on MATH (+0.019 over random mean), AMC (+0.031, about one AMC
problem's worth of samples) and GPQA (+0.008), and lowest on AIME (−0.017, half a problem) and Kaoyan (−0.015). The
largest pass@8 move is AIME −0.100 (3 of 30 problems). None of these is reliable: with two seeds, a per-benchmark
spread of 0.000 only means the seeds tied.

## 7. Discussion and findings

1. **Selection didn't matter measurably at this scale.** Training on 15K clean, hard, topic-balanced math traces gives
   the same Pass@1 as training on 15K random traces that are one-third code, with ~520 truncated traces and 14 test
   overlaps. Full fine-tuning on any 15K R1 traces seems to move the 3B model in the same direction, and the content of
   the subset is a second-order effect next to seed and eval noise.
2. **SFT on R1 traces trades Pass@1 for pass@8.** Every fine-tuned model is below base on Pass@1 avg(LB6) (−0.009 to
   −0.017) and above it on pass@8 (+0.017 to +0.031). The models write long R1-style traces, which makes samples more
   varied: more problems are solved at least once in 8, but each sample is right less often. The gains are concentrated
   in the multiple-choice benchmarks (Kaoyan pass@8 0.528 → 0.60–0.64, GPQA 0.707 → 0.76–0.80), even though the smart
   subset has no multiple-choice data. Short-answer math (AMC, CN-Math, Minerva Pass@1) mostly drops.
3. **The pool is hard for a 3B model.** Over the 67,432 math rows, the base model's pass rate has median 0 and mean
   0.26: it solves none of 4 attempts on more than half the problems (mostly AoPS-style OpenMathReasoning). As a result
   the difficulty band [0, 0.5] is dominated by never-solved problems (71% of the smart subset). The null result is
   consistent with a 3B model learning little from R1 traces on problems far beyond it; a band nearer 0.25–0.75, or the
   untrained `hardest_only` / `filter_only` ablations, would test this.
4. **R1 pseudo-labels are mostly self-consistent.** Among 14,758 answered math rows with several R1 responses, mean
   agreement is 0.917 (median 1.0). In a manual check of 15 disagreeing prompts, about half were genuine
   disagreements (`40` vs `140`) and about half were the same answer in different notation (`n≥4, n≠5` vs `n=4 or n≥6`),
   so our majority filter is conservative. (The grader-log summary of 0.5 also counted code rows, whose empty answers
   never match; it doesn't describe math.)
5. **Most of what separates the smart subset from random is cleaning,** yet cleaning, difficulty and topic balance
   together didn't produce a measurable gain: removing ~4.8K code examples, ~520 truncated traces and 14 contaminated
   rows didn't help or hurt beyond noise. Without the ablations we can't say whether the components cancel out.
6. **Eval cost and fragility dominated the project.** Post-SFT models write 5–15K-token traces × 8 samples, so random_s2's
   eight benchmarks alone took ≈21 h on 2 GPUs (≈42 GPU-hours), and the frozen vLLM 0.6.1 stack failed in five
   distinct ways (§8). This, not training, is why ablations and a second smart seed weren't run.

## 8. Limitations

- **No ablations trained.** `filter_only_s1` (cleaning only) and `filter_difficulty_s1` (+ difficulty) were built and
  committed but not trained, for GPU-queue reasons (decision log, 2026-10-12). We therefore can't attribute any gap to
  a single component (cleaning vs difficulty vs topic balance).
- **One seed for the smart subset.** Variance is measured on the random side only.
- **Difficulty from 4 attempts** with an 8,192-token cap and R1's answer as the label. Pass rates are coarse, and a
  wrong R1 label makes a problem look unsolved.
- **Contamination check is near-verbatim only** (8-gram overlap ≥ 0.5). Paraphrased or translated test questions can
  pass; the 0.3–0.5 near-misses weren't hand-checked.
- **Eval hardware differs between the smart and random models.** Trained models are evaluated on 2 GPUs (tensor
  parallel) to avoid a vLLM CPU-swap crash on long outputs: both random models on 2× A100, `full_method_s1` on 2× L40S
  (Falcon). The base model used 1 GPU (OlympiadBench on 1× H200). Sampling and grading are unchanged, but the same model
  scored 0.009 Pass@1 apart on MATH across the two GPU types (§6.3), which is as large as the smart-vs-random gap.
- **No dev-set results.** The dev evals (AIME 2022–23, HMMT, MATH level 5, GPQA main) didn't run in time. No data,
  checkpoint or hyperparameter was chosen using any score, so the test numbers aren't tuned on, but there is no
  held-out confirmation either.
- **Environments across teammates' accounts** differ in three data-loading packages (`pyarrow`, `datasets`, `pandas`;
  decision log 2026-10-10). Sampling and grading packages are identical.
- **Training runs were raced across accounts**; the kept copy is the first to *finish training*, decided before any
  eval score existed.
- **The official grader slightly undercounts when the machine is busy.** `eval/utils/grader.py` gives each symbolic
  equivalence check 3 s; checks that run over count as wrong. Regrading `random_s2`'s Minerva answers on a quieter machine
  flipped 5 responses (3 problems) from wrong to right, about +1 pt Acc / +0.2 pt Pass@1. The eval is frozen, so the
  official numbers are reported (except random_s1 Minerva, regraded because its official grading never finished,
  §6), but this adds load-dependent noise to every run. The regrade ran on a quiet machine, so it may favour
  random_s1 Minerva by up to about this amount.
- **Eval infrastructure failures, all fixed without touching `eval/`:** an unreadable `tokenizer.json` and missing chat
  template (newer transformers in the training env), forked vLLM workers crashing on 2 GPUs, CPU-swap overflow on long
  outputs, and a vLLM 0.6.1 scheduler assertion under recompute preemption. Each was fixed with a documented environment hook
  (decision log, Oct 15–17), and the affected benchmarks were rerun. One failure wasn't fixed: random_s1's Minerva
  grading hung on every attempt and was regraded offline (§6). Some long benchmarks also hit wall-time limits and were
  rerun with longer ones (random_s2 OlympiadBench took 12 h on 2× A100).
- **Second smart method not trained.** `longest_s1` (the 15K longest clean traces) was proposed but not built or trained
  in time.

## 9. Reproducibility and deviations from the course README

Commands, in order: `env/setup_envs.sh` → `scripts/fetch_data.py` → `scripts/audit_pool.py` → `launch/eval_model.sh base`
→ `scripts/make_random_subsets.py --seeds 1 2` → `launch/score_pool.sh` → `scripts/select_subset.py full_method --seed 1`
→ `scripts/make_config.py <run>` → `EVAL=1 launch/train.sh <run>` → `scripts/collect_results.py`. Teammates rebuild a
committed subset from its row list with `scripts/subset_from_idx.py <name>`, which checks the fingerprint.

Deviations from the course README (only where a step was broken as written) are listed in
[docs/reference/upstream-compliance.md](../docs/reference/upstream-compliance.md): the course LLaMA-Factory snapshot,
torch pinned to 2.6.0+cu126 for flash-attn, the antlr4/latex2sympy2 conflict, `save_total_limit: 1` for disk, 8 GPUs
and a 23 h limit instead of the sample's 1 GPU and 1 h. Every decision with its date and reason is in
[docs/reference/decision-log.md](../docs/reference/decision-log.md).

## Appendix A: Training hyperparameters (all runs)

```yaml
model_name_or_path: Qwen/Qwen2.5-3B-Instruct
stage: sft
finetuning_type: full
deepspeed: examples/deepspeed/ds_z3_offload_config.json
flash_attn: fa2
cutoff_len: 16384
template: qwen
per_device_train_batch_size: 1
gradient_accumulation_steps: 8      # × 8 GPUs → global batch 64
learning_rate: 5.0e-6
num_train_epochs: 3
lr_scheduler_type: cosine
warmup_ratio: 0.0
bf16: true
save_steps: 100
save_total_limit: 1                 # added: disk only
```
