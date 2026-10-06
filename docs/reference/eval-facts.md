---
title: Eval facts
tags: [reference, eval]
---

# Eval facts

← [Home](../00-home.md) · [Step 2](../steps/02-base-eval.md)

The eval is the course's `eval/` folder: vLLM generation plus a SymPy `\boxed{}` grader. **It's fixed; never modify
it** (`scripts/check_eval_frozen.sh` verifies the checksums).

| Benchmark | Problems | Answer type | One problem = |
|---|---|---|---|
| `aime` (AIME 2024) | 30 | integer | 3.3 pts |
| `math` (MATH-500) | 499 | LaTeX expression | 0.2 pts |
| `cn_math_2024` | 30 | LaTeX expression | 3.3 pts |
| `kaoyan` | 199 | mostly multiple-choice letter, **Chinese** | 0.5 pts |
| `amc` (AMC 2023) | 40 | number | 2.5 pts |
| `minerva` | 272 | number / expression | 0.4 pts |
| `olympiadbench` | 675 | number / expression | 0.15 pts |
| `gpqa` (Diamond) | 198 | multiple-choice letter | 0.5 pts |

- **Settings:** temperature 0.6, top-p 0.95, n=8, max_tokens 32768. System prompt: "Please reason step by step, and
  put your final answer within \boxed{}."
- **Metrics:** **Pass@1** (the mean over 8 samples) is our primary metric for the claim. **`Acc` (pass@8: at least one of
  8 right) is the leaderboard metric**, and all of last year's numbers below are Acc. `results.md` reports both.
- **Leaderboard AVG** = AIME25, CN_MATH_24, KAOYAN, AMC, MINERVA, OLYMPIADBENCH, GPQA (not AIME24 or MATH). AIME25
  isn't in `eval/data`, so locally we report **avg(LB6)** over the other six.
- **Cost:** post-SFT models write 5–15K-token traces, so eval is much more expensive than for the base model. We run
  one job per benchmark, in parallel.
- **Re-runs:** an existing results jsonl makes eval skip that benchmark, so each model gets its own
  `eval/outputs/<run>/`.

## Last year's reference numbers (Acc / pass@8: the leaderboard metric)

| Model | AIME24 | AIME25 | MATH | CN | KAOYAN | AMC | MINERVA | OLY | GPQA | AVG |
|---|---|---|---|---|---|---|---|---|---|---|
| Baseline Qwen2.5-3B-Instruct | 0.200 | 0.100 | 0.844 | 0.233 | 0.513 | 0.700 | 0.338 | 0.495 | 0.742 | 0.446 |
| rand1 | 0.167 | 0.100 | 0.834 | 0.367 | 0.482 | 0.725 | 0.349 | 0.499 | 0.631 | 0.451 |
| rand2 | 0.167 | 0.167 | 0.856 | 0.400 | 0.618 | 0.625 | 0.338 | 0.526 | 0.768 | 0.492 |
| best team | 0.233 | 0.233 | 0.900 | 0.433 | 0.688 | 0.800 | 0.346 | 0.569 | 0.606 | 0.525 |

The random seed spread alone was ~4 points of AVG (in pass@8). How do we know these are pass@8? Our base AIME run gave Acc
0.167 (vs 0.200, one problem off) and Pass@1 0.067, which matches Qwen's published ~6.7%. Also, a 3B model can't reach
0.742 Pass@1 on 4-choice GPQA.

## Dev set (for every decision; never the test benchmarks)

`dev/data/`: `aime2223` (AIME 2022–23), `hmmt25` (HMMT Feb 2025), `math_l5` (MATH *train* level 5, 200), `gpqa_main`
(GPQA main minus Diamond, 200, same MC format). It runs through the unmodified `eval/eval.py` with n=4
(`launch/dev_eval.sh`).
