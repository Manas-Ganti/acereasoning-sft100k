---
step: 7
title: Compare against random, write up, submit
status: not-started
depends_on: [6]
outputs: [results/results.md, results/results.csv, report/, HF models + datasets]
deadline: 2026-10-20
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
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py model   random_s2      <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py dataset random_s2      <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py model   full_method_s1 <hf_user>/<repo>
~/.conda/envs/myenv/bin/python scripts/push_to_hub.py dataset full_method_s1 <hf_user>/<repo>
```

## Deliverables checklist (course README §8, verbatim requirements)

Checked against the course README at commit `4d31bfc` on 2026-10-13.

- [ ] Link to the GitHub repository with all necessary files and the final `README.md`
- [ ] Models pushed to Hugging Face (random + advanced)
- [x] **Both** datasets pushed to Hugging Face (random and advanced): `Mrunmayp/acereason-random15k`, `Mrunmayp/acereason-smart15k` (private until submission)
- [ ] Report, which must include:
  - [ ] baseline performance of the original Qwen2.5-3B-Instruct
  - [ ] performance of the fine-tuned model
  - [ ] a comparison and analysis of the results
  - [ ] the hyperparameters used for the final model
  - [ ] a description of the data selection strategy

*Random deliverable = `random_s2`* (the better seed; decision log 2026-10-19). *Not required by the README, but ours:* a second random seed (noise floor) and ablations. Ablations were dropped
(decision log 2026-10-12).

**Other course rules worth knowing:** hyperparameters may be tweaked ("Tweak as needed" in the YAML); data from
other datasets may be added; the live leaderboard counts each team's **best** model on avg pass@8 over AIME25,
CN_MATH_24, KAOYAN, AMC, MINERVA, OLYMPIADBENCH and GPQA (AIME25 is hidden: not in `eval/data`); the top 5 teams get
+10 bonus points. The README deadline reads Oct 14; Manas confirmed Oct 20 on 2026-10-05.

## Rules for the claim

- Compare each run's gap vs the random mean to the **random seed spread**. A gap smaller than the spread is not an
  improvement.
- Report the training-token totals next to the results: smart subsets drop the longest traces.
- Any leaderboard-only tuning (LR/epochs on the winning data) is reported **separately**.
- Spec: [CLAUDE.md, Step 7](../../CLAUDE.md).
