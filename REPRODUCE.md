# Reproducing the project

Full instructions for setup, data, training and evaluation. The report is the [README](README.md).

This repo extends the course repo [reds-lab/Project-Reasoning-SFT-LLM](https://github.com/reds-lab/Project-Reasoning-SFT-LLM)
(commit `4d31bfc`). `LLaMA-Factory/` and `eval/` are copied from it, and `eval/` is byte-identical (checked by
`scripts/check_eval_frozen.sh`). Deviations from the course README, only where a step was broken as written, are listed in
[docs/reference/upstream-compliance.md](docs/reference/upstream-compliance.md).

## Repository layout

| Path | Contents |
|---|---|
| `scripts/` | data audit, pool scoring, subset selection, config generation, results, HF upload |
| `launch/` | SLURM launchers for training, eval and scoring (all sbatch flags in `launch/common.sh`) |
| `env/` | environment setup, checks, and the vLLM hooks needed for long trained-model evals |
| `LLaMA-Factory/` | course snapshot; `yamls/<run>.yaml` training configs, `data/dataset_info.json` |
| `data_subsets/` | each subset's pool row indices (`.idx.txt`) and selection funnel (`.meta.json`) |
| `eval/` | course eval, unmodified; `eval/outputs/<run>/log_<benchmark>.txt` holds every score |
| `docs/` | step notes, run notes, decision log |

## Installation

Two conda environments, built from the course's own requirement files as written. Tested on VT ARC with
`module load Miniconda3 CUDA/12.6.0`.

| Env | Python | Built from | Used for |
|---|---|---|---|
| `myenv` | 3.10 | `LLaMA-Factory/requirements.txt` + torch 2.6.0+cu126, flash-attn | training, embeddings, HF upload |
| `evalenv` | 3.11 | `eval/requirements.txt` (vllm ≤ 0.6.1, sympy 1.12); transformers 4.44.2 | eval, audit, scoring, selection |

```bash
git clone https://github.com/Manas-Ganti/acereasoning-sft100k.git && cd acereasoning-sft100k
bash env/setup_envs.sh          # builds both envs
bash env/check_envs.sh          # verifies versions and imports
# hooks for trained-model evals (2-GPU spawn, CPU swap, swap-only preemption), once per account
bash env/vllm_spawn_hook.sh && bash env/vllm_swap_hook.sh && bash env/vllm_preempt_hook.sh
huggingface-cli login           # needs GPQA access: https://huggingface.co/datasets/Idavidrein/gpqa
```

## Reproducing the results

`PY=~/.conda/envs/evalenv/bin/python`. Every step is a script or a SLURM launcher (`DRY_RUN=1` previews a submission).

```bash
# 1. Data: download the 100K pool and audit it (length, boxed answers, duplicates, contamination)
$PY scripts/fetch_data.py && $PY scripts/build_dev_set.py
launch/cpu.sh python scripts/audit_pool.py

# 2. Base model eval (8 benchmarks, one job each)
launch/eval_model.sh base

# 3. Random subsets: uniform over all 100K, seeds 1 and 2
$PY scripts/make_random_subsets.py --seeds 1 2

# 4. Advanced subset: score the pool with the base model (k=4), cluster prompts, then select
SHARDS=16 launch/score_pool.sh
$PY scripts/select_subset.py full_method --seed 1

# 5. Train (8 GPUs, README YAML; configs differ only in dataset/output_dir) and chain the 8 evals
$PY scripts/make_config.py random_s2 full_method_s1
EVAL=1 launch/train.sh random_s2
EVAL=1 launch/train.sh full_method_s1

# 6. Collect scores from eval/outputs/<run>/log_*.txt
$PY scripts/collect_results.py --from-logs
```

A committed subset can be rebuilt exactly from its row list with `$PY scripts/subset_from_idx.py <name>`, which checks
its sha256 fingerprint.

## Reproducibility details

- **Seeds:** random subsets use `numpy.random.default_rng(seed)` with seeds 1 and 2 (random_s2 is the reported
  baseline). Advanced selection uses seed 1. Eval sampling uses the course eval's fixed seed 0.
- **Subset fingerprints** (sha256 of sorted pool indices): `random_s2` `b55e6eaa…`, `full_method_s1` `d733da24…`.
- **Training:** the course README YAML (`LLaMA-Factory/yamls/_template.yaml`): full fine-tune, ZeRO-3 offload,
  FlashAttention-2, lr 5e-6, 3 epochs, batch 1 × grad-accum 8 × 8 GPUs = 64, cosine, no warmup, cutoff 16,384, bf16.
  8× A100-80GB per run.
- **Eval:** the course `eval_single.sh`, unmodified: temperature 0.6, top-p 0.95, n=8, max 32,768 tokens; 2 GPUs per
  trained-model benchmark (A100 or L40S).
- **Dependencies:** pinned in the two requirement files above; the exact deviations (torch pin, antlr4/latex2sympy2
  conflict, transformers pin) are in [upstream-compliance](docs/reference/upstream-compliance.md).
- **Decisions** with dates and reasons: [docs/reference/decision-log.md](docs/reference/decision-log.md).
