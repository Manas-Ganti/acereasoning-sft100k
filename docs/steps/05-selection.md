---
step: 5
title: Design the selection
status: done
depends_on: [4]
outputs: [LLaMA-Factory/data/<preset>_s<seed>.json, data_subsets/<preset>_s<seed>.meta.json]
cost: CPU, seconds
tags: [step]
---

# Step 5: Design the selection

← [Step 4](04-score-pool.md) · [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 6](06-ablations.md)

**Goal:** a deterministic filter-and-sample procedure over `pool_scores.parquet` that yields exactly 15,000 samples.
Each preset adds one ingredient to the previous one, so the ablations isolate it:

| Preset | Adds | Question it answers |
|---|---|---|
| `filter_only` | math only; drop truncated, no `\boxed{}`, ungradeable or proof, contaminated (test + dev), flagged; one R1 response per prompt | "Is it just dropping code and broken samples?" |
| `filter_difficulty` | + pass_rate in [0, 0.5]; drop 0/8 rows whose R1 answer isn't the R1 majority | does difficulty targeting help? |
| `full_method` | + stratify across topic clusters (equal shares, capped by availability) | does topic balance help? |
| `hardest_only` (optional) | pass_rate = 0 only | is "too hard" harmful at 3B? |

## How

```bash
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/select_subset.py full_method --seed 1 --dry-run     # prints the funnel, writes nothing
$PY scripts/select_subset.py filter_only --seed 1
$PY scripts/select_subset.py filter_difficulty --seed 1
$PY scripts/select_subset.py full_method --seed 1
```

Each run writes `LLaMA-Factory/data/<name>.json`, registered the README way. The funnel and composition go to
`data_subsets/<name>.meta.json`, including `sum_total_tokens`, so the training-token difference vs random can be
reported.

## Done when

All presets produce exactly 15,000 rows. Any band or threshold change is justified on the **dev set**, never the test
benchmarks.

## Results

Built 2026-10-12 on Manas's account, seed 1 (`select_subset.py <preset> --seed 1`). The row lists and meta are
committed. Teammates rebuild them with `scripts/subset_from_idx.py <name>`.

**Funnel (shared by all three presets up to "unique prompts")**

| step | rows | dropped |
|---|---|---|
| pool | 100,000 | |
| math | 67,432 | 32,568 code |
| not truncated (≤16,384) | 64,907 | 2,525 |
| balanced `\boxed{}` in final answer | 64,712 | 195 |
| not proof-like / prose answer | 60,648 | 4,064 |
| not contaminated (test) | 60,586 | 62 |
| not contaminated (dev) | 60,508 | 78 |
| no quality flag | 60,504 | 4 |
| *filter_only:* unique prompts | 53,695 | |
| *difficulty presets:* pass_rate ∈ [0, 0.5] | 47,768 | 12,736 |
| *difficulty presets:* drop pass_rate-0 rows not in the R1 majority | 46,333 | 1,435 |
| *difficulty presets:* unique prompts | 41,626 | |

All three subsets: exactly 15,000 rows, 15,000 unique prompts, no fill rows.

**Composition**

| subset | pass 0 | 0.25 | 0.5 | 0.75 | 1.0 | mean tokens | total tokens | cluster entropy (max 6.64) | largest cluster |
|---|---|---|---|---|---|---|---|---|---|
| `filter_only_s1` | 8,392 (56%) | 2,035 | 1,338 | 1,240 | 1,995 | 7,160 | 107.4M | 6.53 | 2.1% |
| `filter_difficulty_s1` | 10,627 (71%) | 2,605 | 1,768 | — | — | 7,571 | 113.6M | 6.53 | 2.3% |
| `full_method_s1` | 10,612 (71%) | 2,619 | 1,769 | — | — | 7,486 | 112.3M | **6.64** | **1.0%** |

For comparison, a random 15K subset is about 67% math / 33% code, with ~3.5% truncated rows and about 112M tokens
(capped at 16,384).

**Reading it**
- Training tokens are nearly equal across subsets (107–114M vs ~112M random), so compute doesn't confound the comparison.
- `filter_only` → `filter_difficulty` is a **modest** change. 78% of `filter_only` already falls in the band; the
  difficulty step removes the 0.75/1.0 rows (22%) and raises the share of 0/4 problems from 56% to 71%. Expect a small effect.
- `full_method` makes topics exactly uniform (150 rows per cluster, entropy at its maximum log2(100) = 6.64).
- Most of the difference from random is math-only plus no truncation; `filter_only` isolates that.

## Notes

- If fewer than 15K unique prompts survive, extra R1 responses fill the gap, and the meta file logs it.
- Spec: [CLAUDE.md, Step 5](../../CLAUDE.md).
