---
step: 1
title: Audit the 100K pool
status: done
depends_on: [0]
outputs: [analysis/pool_audit.parquet, analysis/pool_audit.md]
cost: CPU, ~15 min
tags: [step]
---

# Step 1: Audit the 100K pool

← [Step 0](00-setup.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 2](02-base-eval.md)

**Goal:** know what is in the pool before choosing from it. Every sample gets these measurements:

| Column | Meaning |
|---|---|
| `domain` | math / code / other (from the dataset's own `extra_info.category`) |
| `resp_tokens`, `total_tokens` | length in **Qwen2.5** tokens (the tokenizer training uses) |
| `truncated` | prompt + response > 16384 = `cutoff_len`. Training would cut the tail, so the model learns to stop without `\boxed{}` |
| `has_boxed`, `r1_answer` | is there a gradeable `\boxed{}` final answer; extracted with the eval's own parser |
| `answer_kind`, `proof_like` | numeric / expression / mc / text. Prose answers can't be graded |
| `prompt_hash`, `dup_count` | the pool has several R1 responses for some prompts |
| `contam`, `contam_bench` | 8-gram overlap with an eval test question (and `contam_dev` for the dev set) |
| `flag_*` | repetition loops, language mixing, malformed think tags |

## How

```bash
launch/cpu.sh python scripts/audit_pool.py      # submits a CPU job (evalenv, tc_normal_short)
# log: logs/slurm/cpu-audit_pool-<jobid>.out
```

## Done when

`analysis/pool_audit.md` exists and its numbers look plausible: about 100K rows, a math/code split, truncation %,
contamination hits.

## Results

✅ Done 2026-10-05 (job after 7864578; full output: [pool_audit.md](../../analysis/pool_audit.md)).

| | math | code |
|---|---|---|
| rows | 67,432 (67%) | 32,568 (33%) |
| unique prompts | 59,702 | 24,391 |
| response tokens p50 / p90 / p99 | 6,641 / 14,238 / 17,712 | 6,120 / 14,004 / 16,302 |
| truncated at 16,384 | 3.7% (2,525) | 2.8% |
| has gradeable `\boxed{}` | 99.3% | n/a |
| quality flags | ~0 (4 repetition, 5 language-mix) | ~0 |

- **Answer kinds (math):** numeric 52%, expression 40%, prose (`text`) 5.4%, multiple-choice 1.9%. 4,176 proof-like
  prompts (6.2%).
- **Duplicates:** about 12.5K of 84K prompts have more than one R1 response, so `r1_agreement` covers only ~10–15%
  of math.
- **Contamination:** 91 rows, all verbatim. AMC 4 (4/40 questions = 10% of AMC), olympiadbench 33 (27 questions),
  MATH-500 54 (19 questions). Dev overlap: 81 rows.
- **Survive the basic filter:** 64,646 math rows (57,350 unique prompts); 60,582 without proof-like.

**Takeaways for the design:**
1. The domain is the big lever. Random 15K ≈ 10K math + 5K code, and no benchmark is code.
2. Quality filters barely matter; the data is already clean apart from truncation.
3. Contamination is small but hits AMC hard.
4. There's almost no multiple-choice or science content, so watch GPQA and kaoyan.
5. There's plenty of room: 57K candidates for 15K slots.

Follow-up: the 8-gram check can't see translated or paraphrased copies (kaoyan, CN-Math). Spot-check rows with
`contam_score` 0.3–0.5 before Step 5.

## Notes

- The flag thresholds were tuned on a 3K-row sample: normal traces have a tail compression ratio of ~0.37, and short
  answers like `\boxed{No}` are legitimate.
- The audit already found a MATH-500 test problem in a 3K-row sample, so contamination is real.
- Spec: [CLAUDE.md, Step 1](../../CLAUDE.md).
