---
title: STATUS
current_step: 1
phase: setup done, starting Step 1
last_updated: 2026-10-05
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
**Next: submit the Step 1 audit, and the Step 2 base eval alongside it.**

## Step board

| # | Step | Status | Gate / key result | Note |
|---|---|---|---|---|
| 0 | Setup | ✅ done | `check_envs` + batch activation test pass | [00-setup](steps/00-setup.md) |
| 1 | Audit pool | ⏭️ next | — | [01-audit-pool](steps/01-audit-pool.md) |
| 2 | Base eval + gate | ⏭️ next | gate: within tolerance of last year's baseline | [02-base-eval](steps/02-base-eval.md) |
| 3 | Random ×2 | ⬜ not started | seed spread = the bar | [03-random-baselines](steps/03-random-baselines.md) |
| 4 | Score pool | ⬜ not started (needs Step 1) | — | [04-score-pool](steps/04-score-pool.md) |
| 5 | Selection | ⬜ not started (needs Step 4) | — | [05-selection](steps/05-selection.md) |
| 6 | Ablations | ⬜ not started | — | [06-ablations](steps/06-ablations.md) |
| 7 | Compare + submit | ⬜ not started | deadline Oct 14, 11:59 PM ET | [07-compare-submit](steps/07-compare-submit.md) |

Legend: ⬜ not started · ⏭️ next · 🔄 running · ✅ done · ⛔ blocked / gate failed

## Running jobs

| Job ID | What | Submitted | Expected | Log |
|---|---|---|---|---|
| — | | | | |

## Next actions

- [ ] Step 1: `launch/cpu.sh python scripts/audit_pool.py` → read `analysis/pool_audit.md`
- [ ] Step 2: `launch/eval_model.sh base` → `scripts/collect_results.py --gate base`
- [ ] Step 4: after the audit finishes, `launch/score_pool.sh`
- [ ] Check `quota` before any training: each run peaks at about 100 GB of checkpoints

## Blockers / open questions

- Disk: `/home` had ~151 GB free before two old repos were deleted, and the quota display updates later. Re-check
  `quota` before Step 3.

## Change log (newest first)

- **2026-10-05**: Docs reorganised into an Obsidian vault (`docs/`). Setup finished on ARC. Solved along the way:
  base-conda leakage into jobs, the torch/flash-attn pin, the transformers pin, the antlr4 conflict, and ARC's `$WORK`
  variable. See [Decision log](reference/decision-log.md) and [ARC guide](reference/arc-guide.md).
- **2026-10-05**: Repo created and pushed to `github.com/Manas-Ganti/acereasoning-sft100k`. SLURM account `tml_2026`.
