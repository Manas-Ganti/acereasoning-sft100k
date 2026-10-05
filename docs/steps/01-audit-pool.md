---
step: 1
title: Audit the 100K pool
status: next
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

*(fill in: math/code counts, % truncated, % has_boxed, # contaminated + which benchmarks, duplicate stats,
how many math rows survive the basic filter)*

## Notes

- The flag thresholds were tuned on a 3K-row sample: normal traces have a tail compression ratio of ~0.37, and short
  answers like `\boxed{No}` are legitimate.
- The audit already found a MATH-500 test problem in a 3K-row sample, so contamination is real.
- Spec: [CLAUDE.md, Step 1](../../CLAUDE.md).
