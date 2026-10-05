---
title: Repo map
tags: [reference]
---

# Repo map

← [Home](../00-home.md)

```
docs/            this vault: home, STATUS, step notes, reference, run notes, templates
eval/            course eval, byte-identical (eval.sha256). NEVER edit.
LLaMA-Factory/   course snapshot. We add: data/<subset>.json + entries in data/dataset_info.json,
                 yamls/ (_template.yaml = README YAML; <run>.yaml generated), saves/ (gitignored)
env/             setup_envs.sh, check_envs.sh, arc_env.sh (every job), clean_conda.sh, diagnose_activate.sh
scripts/         python (below)
slurm/           job bodies: train.slurm, run.slurm (generic), dev_eval.slurm, test_activation.slurm
launch/          submit helpers; all sbatch flags in common.sh
data_subsets/    <name>.meta.json (funnel + composition), <name>.idx.txt (pool rows); json symlinks
analysis/        pool_audit.md, clusters_spotcheck.md (+ gitignored parquet tables)
dev/             dev set (data/<set>/test.jsonl, prompts/)
results/         results.csv / results.md, dev_results.*
work/            (gitignored) pool, generations, embeddings, dev-eval outputs
```

## Scripts → steps

| Script | Step | Env | What it does |
|---|---|---|---|
| `fetch_data.py` | 0 | evalenv | download pool JSON (README 1.5) + base model; build parquet cache |
| `build_dev_set.py` | 0 | evalenv | build `dev/` from AIME, HMMT, MATH-train L5, GPQA main |
| `audit_pool.py` | 1 | evalenv | per-sample audit → `analysis/pool_audit.{parquet,md}` |
| `collect_results.py` | 2, 7 | evalenv | Pass@1 tables, `--gate base`, seed spread, bootstrap CI |
| `make_random_subsets.py` | 3 | evalenv | `random_s<seed>` subsets |
| `make_config.py` | 3, 6 | evalenv | per-run YAML from the README template; `--check` enforces data-only differences |
| `score_pool_generate.py` | 4 | evalenv | vLLM k=8 base-model samples per unique math prompt (sharded array) |
| `score_pool_grade.py` | 4 | evalenv | grade vs R1 answer, R1 agreement → `pool_grades.parquet` |
| `embed_cluster.py` | 4 | myenv | embeddings + k-means → `pool_clusters.parquet`, spot-check |
| `build_pool_scores.py` | 4 | either | join audit + grades + clusters → `pool_scores.parquet` |
| `select_subset.py` | 5 | evalenv | presets `filter_only` / `filter_difficulty` / `full_method` / `hardest_only` |
| `push_to_hub.py` | 7 | myenv | upload model / dataset to HF |
| `common.py` | — | — | paths, constants, eval-grader import, subset writer |

## Launchers

| Launcher | Submits |
|---|---|
| `launch/cpu.sh python scripts/<x>.py` | a CPU job (default env evalenv) |
| `launch/eval_model.sh <base\|run>` | 8 × `eval_single.sh`, one per benchmark (conda-clean) |
| `launch/dev_eval.sh <base\|run>` | dev-set eval |
| `launch/train.sh <run>` | 8-GPU training (`EVAL=1` chains the evals) |
| `launch/score_pool.sh` | Step 4 generation array → grading, + embeddings |
| `launch/test_activation.sh` | 5-min check that `source activate` works in a batch job |
