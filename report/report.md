---
title: "Selecting 15K Reasoning Examples for SFT: Difficulty- and Topic-Aware Selection vs Random"
course: ECE 6514 (Trustworthy ML), Fall 2026
status: final
last_updated: 2026-10-20
---

# Selecting 15K Reasoning Examples for SFT: Difficulty- and Topic-Aware Selection vs Random

**Team:** Manas Ganti, Mrunmay Paratwar, Sahasree Datla
**Code:** https://github.com/Manas-Ganti/acereasoning-sft100k
**Models:** [advanced](https://huggingface.co/manasganti/qwen25-3b-acereason-advanced15k) · [random](https://huggingface.co/Mrunmayp/qwen25-3b-acereason-random15k-s2)
**Datasets:** [advanced](https://huggingface.co/datasets/manasganti/acereason-advanced15k) · [random](https://huggingface.co/datasets/manasganti/acereason-random15k)

## Abstract

We fine-tune Qwen2.5-3B-Instruct on 15K examples chosen from a 100K pool of DeepSeek-R1 reasoning traces
(AceReason-1.1-SFT), and compare a random 15K subset with a selected one. Our selection keeps clean math problems
only, keeps the problems the base model solves at most half the time, and balances 100 topic clusters. With identical
hyperparameters, both fine-tuned models beat the base model on the leaderboard average (pass@8: base 0.544, random
0.566, advanced 0.575). The advanced subset is ahead of random by 0.9 points. That is larger than the gap between our two random seeds
(0.5 points) but smaller than the eval noise we measured (up to 1.8 points for the same model on different GPUs), so
**the selection matches random rather than clearly beating it**.

## 1. Motivation and hypothesis

All benchmarks are math or science with a `\boxed{}` answer, but a random 15K subset of the pool is one third code,
includes traces that training truncates before the answer, and spends many examples on problems the 3B model already
solves. **Hypothesis:** a subset of clean math problems at the edge of the model's ability (solved at most half the
time), balanced across topics, teaches more per example than a random subset, and so beats random at the same
hyperparameters and the same number of examples. This combines the difficulty-based and diversity-based strategies
suggested in the course README.

## 2. Experimental setup

| | |
|---|---|
| Base model | `Qwen/Qwen2.5-3B-Instruct` |
| Pool | `redsgnaoh/acereason11_100k`: 100,000 R1-distilled traces (67,432 math, 32,568 code) |
| Random subset | 15,000 rows drawn uniformly without replacement from all 100K (`numpy.random.default_rng(seed)`, `scripts/make_random_subsets.py`), converted to the course's LLaMA-Factory JSON format and registered in `dataset_info.json` as the README shows |
| Advanced subset | §3 |
| Training | LLaMA-Factory, the course README YAML unchanged (Appendix A); 8× A100-80GB per run |
| Eval | The course `eval/` folder, unmodified (checksum-verified): temperature 0.6, top-p 0.95, 8 samples, 32,768 max tokens, `\boxed{}` grader; one job per benchmark |
| Metric | **pass@8** (at least 1 of 8 samples correct), as on the leaderboard. **AVG** = mean of the six visible leaderboard benchmarks (CN-Math, Kaoyan, AMC, Minerva, OlympiadBench, GPQA); AIME25 is hidden |

The random and advanced runs differ **only in their training data**: same base model, YAML, template, cutoff, GPU
count and eval protocol for base, random and advanced.

**Training runs**

| Run | Subset | Steps | Final train loss | Wall time (8× A100) |
|---|---|---|---|---|
| Random | `random_s2` | 705 | 0.631 | 5 h 28 min |
| Advanced | `full_method_s1` | 705 | 0.569 | 20 h 04 min (slower node; same config) |

## 3. Data selection strategy

An audit of the pool showed four problems with random sampling. A third of the pool is code, which no benchmark tests.
3.7% of traces exceed the 16,384-token training cutoff and get cut before their final answer. 91 rows contain a test
question almost verbatim. And many prompts appear several times with different R1 responses. Our selection
(`scripts/select_subset.py`, deterministic, seed 1) addresses these in four stages:

1. **Clean math only.** Keep math examples that fit in the cutoff, end in a `\boxed{}` answer, aren't proofs, don't
   overlap the test or dev sets, and have no repetition or malformed-output flags.
2. **Difficulty for this model.** The base model attempted every math prompt 4 times, graded against R1's answer
   (≈20.5 A100 GPU-hours). We keep problems with pass rate ≤ 0.5. For never-solved problems, we also drop any where R1's
   own responses disagree on the answer, since the label is then likely wrong.
3. **Topic balance.** We embed prompts (`bge-base-en-v1.5`), run k-means with k=100, and sample equal quotas per
   cluster. No topic exceeds 1% of the subset.
4. **One response per prompt.** The result is 15,000 distinct problems.

| Step | Rows left |
|---|---|
| Pool | 100,000 |
| Math | 67,432 |
| Clean (cutoff, `\boxed{}`, no proofs, no contamination, no flags) | 60,504 |
| Pass rate ≤ 0.5, label check | 46,333 |
| One response per prompt | 41,626 |
| Topic-balanced sample | **15,000** |

| | Random 15K (expected) | Advanced 15K |
|---|---|---|
| Math / code | ≈10.1K / 4.9K | 15,000 / 0 |
| Truncated traces | ≈520 | 0 |
| Test-contaminated rows | ≈14 | 0 |
| Base model never solves (0/4) | — | 71% |
| Training tokens | ≈112M | 112.3M |

The two subsets have the same number of training tokens, so compute is not a confound.

## 4. Results

Pass@8. ★ = counts toward the leaderboard average.

| Model | AIME24 | MATH | ★CN-Math | ★Kaoyan | ★AMC | ★Minerva | ★Olympiad | ★GPQA | **AVG** |
|---|---|---|---|---|---|---|---|---|---|
| Base (Qwen2.5-3B-Instruct) | 0.167 | 0.854 | 0.400 | 0.528 | 0.650 | 0.489 | 0.492 | 0.707 | **0.544** |
| Random 15K | 0.233 | 0.848 | 0.367 | 0.608 | 0.700 | 0.452 | 0.501 | 0.768 | **0.566** |
| Advanced 15K | 0.133 | 0.872 | 0.367 | 0.603 | 0.700 | 0.474 | 0.505 | 0.798 | **0.575** |
| *Advanced − Random* | *−0.100* | *+0.024* | *0.000* | *−0.005* | *0.000* | *+0.022* | *+0.004* | *+0.030* | ***+0.009*** |

We trained two random subsets (seeds 1 and 2) and report the better one (seed 2), which makes it a harder baseline to
beat.

**Is the gap real?** We compare it with three measured sources of noise:

| | AVG pass@8 |
|---|---|
| Random seed 1 / seed 2 | 0.561 / 0.566 |
| Advanced | 0.575 |
| **Advanced − better random seed** | **+0.009** |
| Seed-to-seed spread (AVG) | 0.005 |
| Seed-to-seed spread (largest single benchmark) | 0.033 (CN-Math, 1 problem) |
| Same model, same data, A100 vs L40S (MATH) | 0.018 |
| Same outputs regraded on a quieter machine (Minerva) | 0.011 |

The gap is just above the seed spread on the average, but below the hardware and grader noise on single benchmarks.
With only two random seeds, the spread itself is a rough estimate. Random seed 1's Minerva score is a regrade of
its saved outputs, because the official grading run hung; generation and the grader code are unchanged.

## 5. Comparison and analysis

- **Fine-tuning helps on the leaderboard average.** Random is +2.2 points and advanced +3.1 points over base. The gains
  come from Kaoyan (+8), GPQA (+6 to +9) and AMC (+5). CN-Math drops by one problem for both.
- **Selection doesn't clearly beat random.** The +0.9-point AVG gap is within measured eval noise, so we don't claim
  an improvement. Per benchmark, advanced is ahead on GPQA (+3.0, 6 questions), MATH (+2.4) and Minerva (+2.2),
  level on CN-Math, Kaoyan, AMC and OlympiadBench, and behind on AIME24 (−10 points, which is 3 of 30 problems).
- **Cleaning the data didn't matter at this scale.** The random subset still contains ≈4.9K code examples, ≈520
  truncated traces and ≈14 contaminated rows, and it scores the same. 15K R1 traces seem to transfer similarly
  whatever their mix.
- **The difficulty band may be too hard for a 3B model.** 71% of the advanced subset is problems the base model never
  solved. Imitating R1 on problems far beyond the model's reach may teach it little more than random problems do.
- **The gains are in pass@8, not per-sample accuracy.** Averaged over the same six benchmarks, Pass@1 (mean over the 8
  samples) is 0.272 for base, 0.261 for random and 0.263 for advanced. Fine-tuning at this budget makes the model's 8
  attempts more diverse (more problems solved at least once) without making a single attempt more accurate.

## 6. Limitations and improvements

- **One seed per method.** Variance is measured only on the random side (two seeds), and ablations of the selection
  stages were not trained, so we can't attribute effects to individual stages.
- **Difficulty is coarse.** It comes from 4 attempts with an 8,192-token cap, graded against R1's answer as a
  pseudo-label.
- **Eval hardware differs.** Advanced was evaluated on 2× L40S and random on 2× A100 (whichever cluster's queue was
  free). Sampling and grading are identical, but small numeric differences are possible.
- **Our base scores run higher than last year's** on Minerva (+0.15) and CN-Math (+0.17), and match elsewhere.
  Comparisons within this report use one environment and are unaffected.

**Improvements we would make next:**
- Train the ablations already built (`filter_only_s1`, `filter_difficulty_s1`) to see whether difficulty filtering or
  topic balance helps or hurts on its own, and a second seed of the advanced subset.
- Move the difficulty band toward problems the model sometimes solves (pass rate ¼–½ instead of mostly 0), since 71%
  never-solved problems may be too hard to learn from at 3B.
- Score difficulty with more attempts (k=8) and a longer token cap, for less noisy pass rates.
- Add Chinese and multiple-choice examples, since Kaoyan and GPQA reward formats a math-only subset lacks.

## Appendix A: Hyperparameters (final model and all runs)

The course README YAML, unchanged. Each run's YAML differs only in `dataset` and `output_dir`.

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

Reproduction steps, deviations from the course README and dated decisions are in the repo's
[README](../README.md), [upstream-compliance](../docs/reference/upstream-compliance.md) and
[decision log](../docs/reference/decision-log.md).
