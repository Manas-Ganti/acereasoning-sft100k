---
title: Upstream compliance
tags: [reference]
---

# Upstream compliance

← [Home](../00-home.md) · [Decision log](decision-log.md)

The course repo is [reds-lab/Project-Reasoning-SFT-LLM](https://github.com/reds-lab/Project-Reasoning-SFT-LLM) (commit `4d31bfc`).
**Rule:** its README steps are followed as written. Every difference is listed here, with the reason.

| README step | What the README says | What this repo does |
|---|---|---|
| 1.0 tokens | HF token (read/write), GPQA access, W&B token | same (`env/check_envs.sh` verifies the HF token) |
| 1.1 LLaMA-Factory | `git clone hiyouga/LLaMA-Factory`, `conda create -n myenv python=3.10`, `pip install -r requirements.txt`, `pip install -e ".[torch,metrics]" --no-build-isolation` | env `myenv`: same commands, run on the **LLaMA-Factory snapshot shipped in the course repo** (`LLaMA-Factory/`, v0.9.4.dev0, the tested `requirements.txt`). Current hiyouga main requires Python ≥3.11. **torch pinned to 2.6.0+cu126**: the unpinned `.[torch]` extra now resolves to torch 2.14 built for CUDA 13.0, which has no flash-attn wheel and fails to build against ARC's CUDA 12.6 module (seen on ARC 2026-10-05). No requirement file pins torch. |
| 1.2 eval deps | eval/README: separate env, `python=3.11`, `pip install -r requirements.txt` | env `evalenv`: `eval/requirements.txt` with all its pins kept (the **tested pins win**). It's installed in stages because, as of 2026-10-05, two unpinned lines no longer install as written. Unpinned `transformers` resolves to 5.x, which vLLM 0.6.1 predates, so it's pinned to 4.44.2 (contemporary with vLLM 0.6.1). `flash_attn` can't build inside `pip install -r` (torch isn't available at build time), so it's installed afterwards with `--no-build-isolation`; eval doesn't use it. The file's `antlr4==4.11.1` and `latex2sympy2==1.9.1` pins contradict each other (pip `ResolutionImpossible`, confirmed on ARC). Following the main README, `latex2sympy2` is installed with `--no-deps` and antlr4 is set to 4.9.3 (omegaconf's 4.9.x). |
| 1.3 / 1.4 | `pip install flash-attn --no-build-isolation`; `pip install deepspeed==0.16.8` | same |
| 1.5 data | `hf_hub_download(..., filename="data/acereason11_100k.json")` | same (`scripts/fetch_data.py`), plus a parquet cache of the same rows in the same order |
| 2 base eval | `cd eval; sbatch eval_single.sh <dataset>` with `MODEL` / `OUTPUT_DIR` / `CONDA_ENV` | same: `launch/eval_model.sh` runs exactly that, one job per benchmark. Scheduling flags (account, partition, QOS, GPU type, wall time) go on the sbatch command line because `eval/` is never edited. |
| 3 dataset | random 15K; Alpaca fields `instruction,input,output,system`; file in `LLaMA-Factory/data/`; `{"yourdata": {"file_name": "yourdata.json"}}` in `LLaMA-Factory/data/dataset_info.json` | same. Records have exactly those 4 fields, copied unchanged from the pool. |
| 4 SFT | the README YAML; `FORCE_TORCHRUN=1 llamafactory-cli train yamls/<cfg>.yaml` after `module load Miniconda3`, `module load CUDA/12.6.0`, `source activate myenv` | README YAML verbatim (`LLaMA-Factory/yamls/_template.yaml`): `ds_z3_offload_config.json`, lr 5e-6, 3 epochs, bs 1 × GA 8, warmup 0, cosine, cutoff 16384, `saves/qwen25_3b_instruct/<name>`. Only `dataset` and `output_dir` change per run. **One added key:** `save_total_limit: 1` (disk only; it does not change training). Run on 8 GPUs instead of the sample's 1, with a 23 h limit instead of 1 h (see the known issues in CLAUDE.md). |
| 6 eval | `MODEL=/path/to/model sbatch eval.sh` (or `eval_single.sh` per benchmark) | `eval_single.sh` per benchmark, in parallel, with a fresh `OUTPUT_DIR` per model (`eval/outputs/<run>/`) |
| 7 selection | free choice (difficulty / diversity / LIMOPro) | Steps 4–6 of CLAUDE.md |
| 8 submission | GitHub repo + README, both models and both datasets on HF, report | `scripts/push_to_hub.py`; results tables in `results/` |

**Decision on the system prompt (2026-10-05):** register datasets exactly as the README does. LLaMA-Factory
therefore does not read the JSON's `system` field and trains with the `qwen` template's default system prompt
("You are Qwen, created by Alibaba Cloud. You are a helpful assistant."). Eval uses "Please reason step by step,
and put your final answer within \boxed{}.". This consciously overrides the system-prompt invariant in CLAUDE.md.
It applies identically to every run, so the comparisons stay fair.

**Requirements policy (2026-10-05):** the course repo's tested requirement files are used as written. Our own
analysis scripts add only packages the files don't list (pandas, pyarrow; sentence-transformers, scikit-learn,
wandb in `myenv`). Those are installed under a constraints file frozen from the env, so no tested version moves.

**antlr4 (decided 2026-10-05):** `eval/requirements.txt` can't be installed as written; its antlr4 4.11.1 pin conflicts with
latex2sympy2 1.9.1 (needs 4.7.2), confirmed on ARC. `evalenv` follows the main README instead: `--no-deps latex2sympy2`, with
antlr4 4.9.3.

**Other upstream notes:**
- The README YAML uses `//` comments (invalid YAML), the README writes `git depth -1 clone` (should be `git clone --depth 1`),
  and the sample SLURM script has a 1-hour limit.
