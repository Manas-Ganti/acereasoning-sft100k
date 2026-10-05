# Reasoning SFT data selection: Qwen2.5-3B-Instruct on a 15K subset of AceReason-1.1-SFT

This repo is a superset of the course repo [reds-lab/Project-Reasoning-SFT-LLM](https://github.com/reds-lab/Project-Reasoning-SFT-LLM)
(commit `4d31bfc`). It contains:

- `eval/` and `LLaMA-Factory/`, copied from the course repo.
- Scripts that automate the course README's steps on VT ARC.
- The data-selection study described in [`CLAUDE.md`](CLAUDE.md).

**Rule: the course README's steps are followed as written.** Every place this repo differs from them is listed in
the compliance table below, with the reason.

## Compliance with the course README

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

## Layout

```
eval/            course eval, byte-identical (eval.sha256; scripts/check_eval_frozen.sh). NEVER edit.
LLaMA-Factory/   course snapshot. We add data/<subset>.json, entries in data/dataset_info.json,
                 yamls/ (_template.yaml = README YAML; <run>.yaml generated), saves/ (gitignored)
env/             setup_envs.sh (myenv + evalenv), check_envs.sh, arc_env.sh (sourced by every job)
scripts/         fetch, audit, scoring, clustering, selection, configs, results, hub upload
slurm/           job bodies: train.slurm (= run_training.sh), run.slurm (generic), dev_eval.slurm
launch/          submit helpers; all sbatch flags (account / partition / QOS / GPU type) live in common.sh
data_subsets/    <name>.meta.json (selection funnel and composition), <name>.idx.txt (pool rows)
analysis/        pool_audit.md, clusters_spotcheck.md (+ gitignored parquet tables)
dev/             held-out dev set (AIME 22-23, HMMT 25, MATH-train L5, GPQA non-Diamond)
results/         results.csv / results.md (test), dev_results.*
work/            (gitignored) pool, generations, dev outputs
```

## One-time setup (ARC login node)

```bash
git clone <this repo> ~/acereasoning-sft100k && cd ~/acereasoning-sft100k
bash env/setup_envs.sh                      # myenv (README 1.1/1.3/1.4) + evalenv (eval/README)
module load Miniconda3 && source activate evalenv   # interactive scripts below run in evalenv
HF_HOME=/home/$USER/hf_cache huggingface-cli login   # the token must live under HF_HOME
wandb login
bash env/check_envs.sh                      # must print ALL CHECKS PASSED
python scripts/fetch_data.py                # README 1.5 + base model
python scripts/build_dev_set.py             # dev/ (before the audit, so contam_dev is filled)
```

Which env runs what: `evalenv` runs `eval_single.sh` (as `CONDA_ENV=~/.conda/envs/evalenv`: on ARC, `source activate` only works with the absolute path), dev eval, audit, pool scoring/grading,
selection and results. `myenv` runs training, prompt embeddings and HF upload. The launchers pick the env for each job.

Scheduling knobs, set per command: `GPU=h200|a100` (default h200), `ACCOUNT=` (default `tml_2026`, with access to both
A100 and H200), `QOS=` (default `tc_<gpu>_normal_short`; `QOS=none` omits it), `MAIL_USER=`, and `DRY_RUN=1` (print the sbatch lines, submit nothing). Jobs use the `*_normal_short`
QOS (highest priority, 1-day cap). Logs go to `logs/slurm/<job-name>-<id>.out`.

## The sequence (CLAUDE.md steps)

GPU-hours are for H200 and are rough estimates; A100 takes about 2× as long.

| step | command | cost |
|---|---|---|
| **1 audit** | `launch/cpu.sh python scripts/audit_pool.py` → `analysis/pool_audit.{parquet,md}` | CPU, ~15 min |
| **2 base eval** | `launch/eval_model.sh base`, then `python scripts/collect_results.py --gate base`. **If the gate fails, stop.** | ~1 GPU-h |
| **4 score pool** (critical path, start day 1) | `SHARDS=16 launch/score_pool.sh` (k=8 generation → grading → `pool_scores.parquet`, with embeddings + k-means in parallel); then read `analysis/clusters_spotcheck.md` | ~6–10 GPU-h + CPU |
| **3 random ×2** | `python scripts/make_random_subsets.py --seeds 1 2`; `python scripts/make_config.py random_s1 random_s2`; `EVAL=1 launch/train.sh random_s1` (and `random_s2`) | per run: training (ZeRO-3 offload is slower than plain ZeRO-3; time the first run) + ~3 GPU-h eval |
| **5 select** | `python scripts/select_subset.py <preset> --seed 1 [--dry-run]` for `filter_only`, `filter_difficulty`, `full_method`, (`hardest_only`) | CPU, seconds |
| **6 ablations** | `python scripts/make_config.py <run>`; `EVAL=1 launch/train.sh <run>` | same as Step 3 |
| **7 compare** | `python scripts/collect_results.py` (and `--dev`); `python scripts/push_to_hub.py model|dataset <run> <repo>` | |

`EVAL=1 launch/train.sh <run>` submits training and then, with `afterok` dependencies, the 8 `eval_single.sh` jobs
and a dev-set job. Re-submitting is safe: training resumes from the newest checkpoint, and eval skips benchmarks
that already have a jsonl.

## Design notes for the selection study

- **Seed** means the subset-sampling seed. Training uses the README YAML's defaults for every run, and the
  hardware is always 8 GPUs (global batch 1 × 8 × 8 = 64). `train.slurm` refuses any other GPU count.
- **Random subsets** are uniform over the full pool, including code and traces truncated at 16384 tokens. That
  is the README's baseline. The `filter_only` ablation measures how much of any gain comes from the filtering
  alone.
- **Pool scoring** uses eval's chat template, system prompt, temperature 0.6, top-p 0.95, and k=8.
  `max_tokens` is 8192 to keep cost down; capped samples count as failures. `pass_rate` is graded against each
  row's own R1 answer with `eval/utils/grader.py`.
- **The smart presets drop rows that cannot be graded** (prose `\boxed{\text{...}}` answers and proofs), keep
  one R1 response per prompt, and log the full funnel in `data_subsets/<name>.meta.json`, including
  `sum_total_tokens`. Smart subsets drop the longest traces, so report token totals next to the results.
- **Dev set**: every selection choice is made on `dev/`, never on the 8 test benchmarks. The leaderboard also
  scores AIME25, which is not in `eval/data`.
- **Reporting**: `results/results.md` gives Pass@1 per benchmark, `avg(LB6)` (the leaderboard average without
  AIME25), each run's gap vs. the random mean, the **random seed spread**, and a bootstrap CI. A gap smaller than
  the seed spread is not an improvement. Watch `gpqa` and `kaoyan` (multiple-choice), and `boxed_rate`.
