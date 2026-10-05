---
step: 7
title: Compare against random, write up, submit
status: not-started
depends_on: [6]
outputs: [results/results.md, results/results.csv, report/, HF models + datasets]
deadline: 2026-10-14 23:59 ET
tags: [step, deliverable]
---

# Step 7: Compare against random, write up, submit

← [Step 6](06-ablations.md) · [Home](../00-home.md) · [STATUS](../STATUS.md)

**Goal:** an honest, noise-aware comparison, and the course deliverables.

## How

```bash
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/collect_results.py          # results/results.md: table + gap vs random + seed spread + bootstrap CI
$PY scripts/collect_results.py --dev    # results/dev_results.md
# HF uploads (run in myenv):
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py model   random_s1      <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py dataset random_s1      <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py model   full_method_s1 <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py dataset full_method_s1 <hf_user>/<repo>
```

## Deliverables checklist (course README §8)

- [ ] GitHub repo with all scripts, configs, and a final README
- [ ] HF: random-subset model + smart-subset model
- [ ] HF: both 15K datasets (random + smart)
- [ ] Report:
  - [ ] base results
  - [ ] random results (both seeds)
  - [ ] final model results
  - [ ] comparison and analysis, with the noise stated
  - [ ] hyperparameters
  - [ ] selection strategy, with ablations

## Rules for the claim

- Compare each run's gap vs the random mean to the **random seed spread**. A gap smaller than the spread is not an
  improvement.
- Report the training-token totals next to the results: smart subsets drop the longest traces.
- Any leaderboard-only tuning (LR/epochs on the winning data) is reported **separately**.
- Spec: [CLAUDE.md, Step 7](../../CLAUDE.md).
