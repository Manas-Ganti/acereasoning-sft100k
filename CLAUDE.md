# CLAUDE.md — Reasoning SFT Data Selection (ECE 6514)

## What this project is

Supervised fine-tuning of **Qwen/Qwen2.5-3B-Instruct** on a **15K subset** chosen from a fixed
**100K pool** of AceReason-1.1-SFT (NVIDIA; all responses distilled from DeepSeek-R1, math + code).

**The research question:** does a smart 15K subset beat a random 15K subset, at identical
hyperparameters, by more than seed noise?

- Upstream repo: https://github.com/reds-lab/Project-Reasoning-SFT-LLM (commit `4d31bfc`).
  **Its README steps are followed literally and win over this file where they conflict.** Every
  deviation (only where a step is literally broken) is listed in README.md's compliance table.
- Pool: HF dataset `redsgnaoh/acereason11_100k`, file `data/acereason11_100k.json`
  (already in Alpaca format: `instruction`, `input`, `output`, `system`)
- Training: LLaMA-Factory, the snapshot shipped in the course repo (`LLaMA-Factory/`), with the README's
  YAML verbatim (full fine-tune, `ds_z3_offload_config.json`, FlashAttention 2)
- Eval: the repo's `eval/` folder (vLLM generation + SymPy `\boxed{}` grader). **Fixed. Never modify.**
- Deadline: **Wed Oct 14, 2026, 11:59 PM ET.** No late submissions.

---

## THE SEQUENCE (follow in order; respect the gates)

### Step 1 — Audit the 100K pool
For every sample, compute and save to `analysis/pool_audit.parquet`:
- `domain`: math / code / other
- `resp_tokens`: response length using the **Qwen2.5 tokenizer** (not R1's, not tiktoken)
- `truncated`: `resp_tokens` + prompt > 16384 (the training `cutoff_len`)
- `has_boxed`: response ends with a parseable `\boxed{}`; also store the extracted answer
- `prompt_hash`: for detecting duplicate prompts (pool has multiple R1 responses per prompt)
- `contam`: n-gram overlap with any `eval/data/*/test.jsonl` question (check Kaoyan and CN Math especially)

Output: `analysis/pool_audit.md`, a one-page summary of the distributions.

### Step 2 — Evaluate the BASE model (no training)
- Run `eval/eval_single.sh <benchmark>` for all 8 benchmarks, **one GPU/job per benchmark in parallel**.
- **Gate:** the numbers must land near last year's baseline (avg ≈ 0.446; MATH ≈ 0.84, GPQA ≈ 0.74,
  AMC ≈ 0.70, OlympiadBench ≈ 0.50). If they are far off, the eval environment is broken.
  STOP and fix it before any training comparison.

### Step 3 — Random baseline, TWO seeds (the noise floor)
- Sample two random 15K subsets (seed 1, seed 2) from the pool, train each, eval each.
- Last year two random runs scored 0.451 and 0.492. The seed spread alone is ~4 points.
  One random run is NOT a baseline.
- The hyperparameters used here are **frozen** for every comparison run in Step 6. They are the README YAML
  (`LLaMA-Factory/yamls/_template.yaml`: lr 5e-6, 3 epochs, bs 1 x GA 8, warmup 0, cosine, cutoff 16384),
  always on 8 GPUs (global batch 64). Per-run YAMLs differ only in `dataset` and `output_dir`.

### Step 4 — Score every prompt in the pool
Build `analysis/pool_scores.parquet`, one row per sample, extending the audit table:
- `pass_rate`: Qwen2.5-3B-Instruct, k=8 samples per prompt (vLLM, temperature 0.6, top-p 0.95,
  same system prompt as eval), graded against **R1's boxed answer** with `eval/utils/grader.py`.
- `r1_agreement`: where a prompt has multiple R1 responses, fraction agreeing on the final answer.
  R1's answer is a pseudo-label, not ground truth; low agreement = likely label noise.
- `cluster_id`: k-means (k ≈ 50–200) on sentence embeddings of the prompt. Spot-check clusters by hand.
- `flags`: repetition loops, language mixing, malformed output.

This is the slowest step and the critical path. **Start it on Day 1–2**, in parallel with Steps 1–3
(it depends only on the pool and the base model, not on any training).

### Step 5 — Design the selection
Selection = a filter + sampling procedure over `pool_scores.parquet`. The working hypothesis:
1. Math only (the eval has no code benchmarks)
2. Drop `truncated`, `!has_boxed`, `contam`, flagged samples
3. Keep the band Qwen-3B *sometimes* fails (pass_rate ≈ 0 to 0.5); drop 0/8 prompts with low `r1_agreement`
4. Stratify sampling across `cluster_id` so no topic dominates
5. Exactly 15,000 samples

Every selection script must be deterministic (fixed seed). Output: `LLaMA-Factory/data/<name>.json` (README
section 3; `data_subsets/<name>.json` is a symlink to it), with the selection funnel in
`data_subsets/<name>.meta.json` and the pool rows in `data_subsets/<name>.idx.txt`.

### Step 6 — Train smart subset + ablations, then eval
Same frozen hyperparameters, same template, same system prompt, same fixed eval as Step 3.

| Run | Isolates |
|---|---|
| `filter_only` | domain + length/quality filter only ("is it just dropping code?") |
| `filter_difficulty` | + pass-rate band |
| `full_method` | + cluster stratification |
| `hardest_only` (optional) | pass_rate = 0 only; does "too hard" hurt at 3B? |

If time allows, run `full_method` with a second seed so the claim is method-vs-random with variance on both sides.

### Step 7 — Compare against random, write up, submit
- Result table: base, random s1, random s2, every ablation, final, across all 8 benchmarks + avg.
- The claim must account for noise: the gap vs random must be compared to the random seed spread.
- Optional separate track: tune LR/epochs on the winning data for the leaderboard.
  Report it **separately** so it does not contaminate the data-selection comparison.

---

## Invariants (never violate)

- **Never modify anything in `eval/`.** Not prompts, not the grader, not sampling settings.
- **Never select data, checkpoints, or hyperparameters using the 8 test benchmarks.** Use a separate
  dev set (`dev/`): e.g. AIME 2022–23, HMMT, MATH-train level 5, non-Diamond GPQA.
  The leaderboard also scores **AIME25, which is not in `eval/data`**; overfitting to the visible eight shows up there.
- **Comparison runs differ only in data.** Same base model, hyperparameters, template, cutoff, seed handling.
- **System prompt (decided 2026-10-05):** datasets are registered exactly as the README does
  (`{"<name>": {"file_name": "<name>.json"}}`). LLaMA-Factory therefore ignores the JSON's `system`
  field and trains with the qwen template default ("You are Qwen, created by Alibaba Cloud. You are a
  helpful assistant."), while eval uses `Please reason step by step, and put your final answer within \boxed{}.`
  This is deliberate and identical for every run. Do not "fix" it with a `columns` map.
- Every subset is exactly 15,000 samples drawn from the 100K pool (unless a run is explicitly
  documented as adding external data, which the assignment allows but makes comparison harder).

## Eval facts

- 8 benchmarks: `aime` (30), `math` (499), `cn_math_2024` (30), `kaoyan` (199), `amc` (40),
  `minerva` (272), `olympiadbench` (675), `gpqa` (198).
- Leaderboard AVG uses: AIME25, CN_MATH_24, KAOYAN, AMC, MINERVA, OLYMPIADBENCH, GPQA (not AIME24 or MATH).
- Settings: temp 0.6, top-p 0.95, n=8, max_tokens 32768. Logs report pass@8 ("Acc") and **Pass@1** (avg over 8).
  **Pass@1 is the number to compare.**
- `gpqa` and most of `kaoyan` are **multiple-choice with a letter answer** in `\boxed{}`; kaoyan is in Chinese.
  Pure-math SFT can degrade these. Watch them in every run.
- Small benchmarks are noisy: one AIME/CN Math problem = 3.3 pts, one AMC problem = 2.5 pts.
- Post-SFT models write long R1-style traces (5–15K tokens), so eval becomes far more expensive than
  base-model eval. Budget GPU-hours; parallelize by benchmark.
- Outputs: `$OUTPUT_DIR/log_<benchmark>.txt`; per-sample results in `$OUTPUT_DIR/<model>/<benchmark>/*.jsonl`.
  An existing jsonl causes that benchmark to be skipped (use a fresh OUTPUT_DIR per model).

## Known bugs in the upstream README

- The sample YAML uses `//` comments, which are invalid YAML. Use `#`.
- `git depth -1 clone` should be `git clone --depth 1`.
- The training SLURM script has a 1-hour limit; full SFT on 15K long traces needs much more.
- Main README says Python 3.10 + latest vLLM; `eval/README.md` pins `vllm<=0.6.1`, Python 3.11,
  `sympy==1.12`, `antlr4-python3-runtime==4.11.1`. Resolved: two envs built from the **tested requirement
  files as written** (never re-pin them): `myenv` (py3.10, LLaMA-Factory/requirements.txt) for training and
  embeddings; `evalenv` (py3.11, eval/requirements.txt) for eval, audit, scoring and selection.
- Current hiyouga/LLaMA-Factory main needs Python >=3.11, and unpinned `vllm` now pulls transformers 5.x,
  so the course repo's LLaMA-Factory snapshot is used. torch is pinned to 2.6.0+cu126 in myenv (unpinned
  torch now pulls 2.14/CUDA 13.0 -> flash-attn has no wheel and won't build against CUDA/12.6.0).
- On ARC, `source activate <env>` (Miniconda3 25.11 module) can silently leave the base python active:
  setup calls each env's python by absolute path; jobs pin PATH; PYTHONNOUSERSITE=1 everywhere.
- Watch item: locally, `antlr4-python3-runtime==4.11.1` + `latex2sympy2==1.9.1` did not resolve, and
  latex2sympy2 did not import. If evalenv shows the same, `env/setup_envs.sh` stops and reports it; the
  main README's `--no-deps` route (antlr4 4.9.x) is known to work. Ask before changing a pin.
- `cutoff_len: 16384` silently truncates long R1 traces → model learns to stop without `\boxed{}`.
  Handle in Step 1/5, do not ignore.

## Cluster

- VT ARC (Tinkercliffs: `h200_normal_q`, `a100_normal_q`), account **`tml_2026`** (access to both A100 and H200;
  not the README's `ece_6514`). All sbatch flags live in `launch/common.sh` (`GPU=a100|h200`, `QOS=`, `DRY_RUN=1`).
- `module load Miniconda3 && module load CUDA/12.6.0`.
- Training: one full 8-GPU node per run, `FORCE_TORCHRUN=1 llamafactory-cli train yamls/<run>.yaml` from
  `LLaMA-Factory/` (`launch/train.sh`). Eval: `sbatch eval_single.sh <bench>` from `eval/`, one job per
  benchmark, in parallel (`launch/eval_model.sh`).
- Logging: `report_to: wandb`. One W&B project; run name = subset name + seed.

## Suggested layout

```
analysis/        pool_audit.*, pool_scores.parquet, plots
data_subsets/    <name>.meta.json / .idx.txt (+ symlinks to LLaMA-Factory/data/<name>.json)
dev/             held-out dev set (never the 8 test benchmarks)
LLaMA-Factory/   course snapshot; data/<subset>.json, data/dataset_info.json, yamls/<run>.yaml, saves/
scripts/         audit, scoring, selection, slurm launchers
results/         results.csv / results.md (raw eval outputs: eval/outputs/<run>/)
report/          final write-up
```

Register each subset in `LLaMA-Factory/data/dataset_info.json` as `{"<name>": {"file_name": "<name>.json"}}`
(done by `scripts/common.py:write_subset`; see the system-prompt invariant above).

## Deliverables (Step 7)

- GitHub repo with all scripts, configs, and a final README
- HF Hub: the random-subset model, the smart-subset model, and both 15K datasets
- Report: base results, random results (both seeds), final model results, comparison and analysis,
  final hyperparameters, and a description of the selection strategy (with ablations)

## Working style

- Report numbers as tables. State noise explicitly; do not call a gap smaller than the random seed
  spread an improvement.
- Before launching any expensive job (scoring, training, full eval), state the estimated GPU-hours.
- If a step's gate fails, stop and report rather than continuing on a broken baseline.