---
title: Decision log
tags: [reference, decisions]
---

# Decision log

← [Home](../00-home.md) · [STATUS](../STATUS.md)

Every deliberate choice that affects results or reproducibility, newest first. **Add an entry whenever you decide
something; don't silently change behaviour.** Format: what was decided, why, and who decided.

> [!NOTE]
> Standing policy: the course README's steps are followed literally and win over CLAUDE.md where they conflict.
> The course repo's tested requirement files are used as written. We deviate only where a step is literally broken,
> and each deviation is listed in [Upstream compliance](upstream-compliance.md).

---

### 2026-10-05: The leaderboard metric is pass@8; the gate compares Acc
The base AIME run gave Acc 0.167 (last year 0.200, one problem apart) but Pass@1 0.067 (Qwen reports ~6.7%), and
GPQA's 0.742 can't be Pass@1 for a 3B model. So last year's table, the 0.446 baseline and the 0.451/0.492 random
runs are **pass@8**. The Step 2 gate now compares Acc. Pass@1 stays the primary metric for our smart-vs-random
claim (lower variance), and `results.md` reports both metrics with a seed spread for each.

### 2026-10-05: A100 by default
The H200 queue estimated a 4-day wait for 1-GPU eval jobs. A100s are the default (`GPU=h200` to override); every
compared run should use the same GPU type.

### 2026-10-05: antlr4 4.9.3 in evalenv (main README route)
`eval/requirements.txt` pins `antlr4-python3-runtime==4.11.1` and `latex2sympy2==1.9.1`, which cannot coexist:
pip raises `ResolutionImpossible` on ARC, and under 4.11.1 latex2sympy2 can't even be imported. We follow the main
README instead: `pip install --no-deps latex2sympy2==1.9.1` with antlr4 4.9.3 (omegaconf's 4.9.x). The grader check
passes. *Decided by: Manas.*

### 2026-10-05: transformers 4.44.2 in evalenv
`transformers` is unpinned in `eval/requirements.txt` and now resolves to 5.x, which vLLM 0.6.1 predates. We pin the
release that was current alongside vLLM 0.6.1. `flash_attn` is installed after torch with `--no-build-isolation`;
eval never imports it.

### 2026-10-05: torch 2.6.0+cu126 in myenv
Unpinned torch (from LLaMA-Factory's `.[torch]` extra) now resolves to 2.14 built for CUDA 13.0. flash-attn has no
wheel for it and can't build against ARC's CUDA 12.6 module. 2.6.0+cu126 matches the module, has a prebuilt
flash-attn wheel, and is proven on these nodes. No requirement file pins torch.

### 2026-10-05: Two environments, built from the tested requirement files
`myenv` (py3.10): `LLaMA-Factory/requirements.txt` + README §1.1/1.3/1.4. `evalenv` (py3.11): `eval/requirements.txt`
(eval/README). Extra analysis packages are added only under a frozen-constraints install. *Decided by: Manas.*

### 2026-10-05: Datasets registered exactly as the README does → Qwen default system prompt in training
`{"<name>": {"file_name": "<name>.json"}}` only. With this registration LLaMA-Factory ignores the JSON's `system`
field and trains with the `qwen` template default ("You are Qwen, created by Alibaba Cloud. You are a helpful
assistant."), while eval uses "Please reason step by step, and put your final answer within \boxed{}.". This is
deliberate, identical across all runs, and overrides CLAUDE.md's original invariant. **Do not "fix" it with a
`columns` map.** *Decided by: Manas.*

### 2026-10-05: Training = the README YAML verbatim
ZeRO-3 offload, lr 5e-6, 3 epochs, bs 1 × GA 8, warmup 0, cosine, cutoff 16384, output under
`saves/qwen25_3b_instruct/`. Every comparison run uses 8 GPUs (global batch 64). The only added key is
`save_total_limit: 1`, which saves disk and doesn't change training.

### 2026-10-05: The course's LLaMA-Factory snapshot, not hiyouga main
Current hiyouga main requires Python ≥3.11, which contradicts the README's `python=3.10`. The course repo ships a
snapshot (v0.9.4.dev0), and the README's own links point to it.

### 2026-10-05: SLURM account `tml_2026`
It has A100 and H200 access (QOS `tc_a100_normal_short`, `tc_h200_normal_short`, and `tc_normal_short` for CPU jobs).
This replaces the README's `ece_6514`. *Decided by: Manas.*

### 2026-10-05: Selection design (proposal, to be confirmed with Step 4 data)
- Math only.
- Drop truncated, ungradeable, proof-like, contaminated (test + dev) and flagged rows.
- Keep pass_rate in [0, 0.5], and drop 0/8 rows that disagree with the R1 majority.
- Stratify across 100 clusters.
- One R1 response per prompt.

Any change to thresholds must be justified on the **dev set**.

### 2026-10-05: "Seed" means the subset-sampling seed
The training seed is the HF default for every run. `random_s1` vs `random_s2` measures data-sampling noise plus
training nondeterminism.

### 2026-10-09: Step 4 scores with k=4 base-model attempts per prompt, not 8
CLAUDE.md specifies k=8. With 1-GPU jobs waiting days, k=4 halves generation (about 5–12 instead of 10–25 A100
GPU-h). pass_rate then takes values 0, 0.25, 0.5, 0.75, 1, which still separates never / sometimes / always solved.
The selection rule needs only that. The "drop 0/8 rows with low R1 agreement" rule becomes "drop 0/4 rows".
`SAMPLES=8 launch/score_pool.sh` restores k=8. *Decided by: Manas.*

### 2026-10-09: vLLM CPU swap space raised in our scoring script
`scripts/score_pool_generate.py` passes `swap_space=32` (GiB; `--swap-gb`). The base OlympiadBench eval aborted with
"Aborted due to the lack of CPU swap space" at vLLM's 4 GiB default, and scoring also samples n>1 per prompt.
This affects memory only, not sampling. The frozen `eval/` is untouched; for evals the workaround is 2 GPUs (tensor parallel).

