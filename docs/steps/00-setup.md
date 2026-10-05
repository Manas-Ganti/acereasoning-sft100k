---
step: 0
title: Setup on ARC
status: done
depends_on: []
outputs: [myenv, evalenv, work/pool/pool.parquet, dev/]
tags: [step]
---

# Step 0: Setup on ARC

← [Home](../00-home.md) · [STATUS](../STATUS.md) · next: [Step 1](01-audit-pool.md)

**Goal:** working environments, the 100K pool, the base model and the dev set on VT ARC (Tinkercliffs).

## How

```bash
git clone git@github.com:Manas-Ganti/acereasoning-sft100k.git && cd acereasoning-sft100k
git config user.name "<your name>" && git config user.email "<your GitHub email>"   # so commits are attributed to you
bash env/setup_envs.sh          # myenv (training) + evalenv (eval), ~30 min
HF_HOME=/home/$USER/hf_cache ~/.conda/envs/evalenv/bin/huggingface-cli login   # accept GPQA terms on HF first
bash env/check_envs.sh          # must end with ALL CHECKS PASSED
launch/test_activation.sh       # 5-min batch job: both envs must show sys.executable inside ~/.conda/envs/<env>
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/fetch_data.py       # README 1.5: pool JSON (2.5 GB) + parquet cache + base model
$PY scripts/build_dev_set.py    # dev set: AIME 22-23, HMMT 25, MATH-train L5, GPQA non-Diamond
```

## Done when

- `check_envs.sh` prints `ALL CHECKS PASSED`
- the activation test shows the right `sys.executable` for both envs
- `fetch_data.py` prints `pool: 100000 rows`
- `dev/manifest.json` lists the four dev sets

## Result

✅ Done 2026-10-05 (account `tml_2026`).

## Pitfalls already solved

All of them are documented in the [ARC guide](../reference/arc-guide.md):
- base conda leaking into jobs
- `source activate` not switching interpreters
- the torch/flash-attn pin
- the cross-device rename
- `$WORK=/notavailable`
- the antlr4 conflict
