---
title: ARC guide and gotchas
tags: [reference, arc]
---

# ARC guide and gotchas

← [Home](../00-home.md) · [STATUS](../STATUS.md)

## Basics

| | |
|---|---|
| Cluster | VT ARC **Tinkercliffs** (`tinkercliffs1/2.arc.vt.edu`) |
| Account | **`tml_2026`**: A100 + H200 access |
| GPU partitions / QOS | `h200_normal_q` + `tc_h200_normal_short`, `a100_normal_q` + `tc_a100_normal_short` (top priority, 1-day cap) |
| CPU partition / QOS | `normal_q` + `tc_normal_short` |
| Repo on ARC | `~/ondemand/data/acereasoning-sft100k` (Manas's checkout) |
| Envs | `~/.conda/envs/myenv` (training), `~/.conda/envs/evalenv` (eval / scoring) |
| HF cache + token | `HF_HOME=/home/$USER/hf_cache` (the token must live under it) |
| Workflow | edit on laptop → `git push` → `git pull` on ARC → submit with `launch/*.sh` |

All scheduling flags live in `launch/common.sh`. Knobs, set per command:
- `GPU=h200|a100`
- `QOS=…` or `QOS=none`
- `ACCOUNT=…`
- `MAIL_USER=…`
- `DRY_RUN=1` prints the sbatch lines without submitting

Logs go to `logs/slurm/<job-name>-<jobid>.out`.

```bash
squeue -u $USER -o "%.10i %.20j %.9T %.11M %.11L %.22R %N"
sacct -j <id> --format=JobID,JobName%25,State,Elapsed,MaxRSS,ExitCode
quota                      # /home is 640 GB total
```

## Disk budget

- **Permanent:** ~90 GB by the end (envs ~20, pool ~3.5, 7 models × 6 GB, eval outputs ~15).
- **Training peak:** each running training adds **~100 GB** (two ~45–50 GB ZeRO-3 checkpoints with optimizer state
  during a save). `train.slurm` deletes checkpoints after a successful run.
- **Rule:** check `quota` before every training submission, and run trainings in parallel only if there's room.

## Gotchas already solved (don't re-debug these)

> [!WARNING]
> **`source activate` in batch jobs picked the wrong Python.** The login shell has a personal `~/miniconda3` base
> active (conda init, `auto_activate: True`), and sbatch copies that state into the job. `eval_single.sh`'s
> `module load Miniconda3` puts the module's base `bin` in front, and `conda activate` only replaces the
> *previously active* prefix's PATH entries, so the module's base Python 3.13 stays first.
> **Fix:** launchers submit eval jobs from a conda-clean environment (`env/clean_conda.sh`). Verified with
> `launch/test_activation.sh`. Our own job bodies never use `source activate`: `env/arc_env.sh` sets
> `PY`/`PATH` from the env named by `SFT_ENV` and checks a sentinel import.

- **`CONDA_ENV` is taken:** `~/.bashrc` exports `CONDA_ENV=~/miniconda3/envs/vrr` (the VLM project), and the first
  audit job (7864578) ran in it. Our launchers select envs with **`SFT_ENV`** (`myenv`/`evalenv`, always set
  explicitly), and `arc_env.sh` refuses anything else and runs a sentinel import every time. The log line
  `[arc_env] ... env=evalenv python=/home/manasganti/.conda/envs/evalenv/bin/python` confirms the right env.
- **`conda env list` / `conda info` aren't evidence** of which Python runs. Check `sys.executable`.
- **ARC sets `$WORK`** (`/notavailable` without a work allocation). Our scripts use `SFT_WORK_DIR` instead.
- **`pip` missing the env:** inside `setup_envs.sh`, pip ran from base and installed into `~/.local`. Every pip call
  now goes through the env's own Python by absolute path, with `PYTHONNOUSERSITE=1`.
- **flash-attn `Invalid cross-device link`:** `/tmp` and `/home` are different filesystems. Install with `TMPDIR`
  on `/home`.
- **Unpinned torch → 2.14/CUDA 13.0**, which has no flash-attn wheel. Pinned 2.6.0+cu126 (see the
  [decision log](decision-log.md)).
- **Zero-byte interpreter** (seen in another project): if a job "succeeds" in seconds with an empty log, run
  `python -V` first.
- **NCCL on H200:** `ib0` exists but has no IPv4. `arc_env.sh` picks an interface with an address.
- **Never use `--mem=0` on partial-node jobs** (they can't backfill). Full-node training uses it deliberately.
- **`.slurm` files are copied at submit time.** A pending job won't see later edits; cancel and resubmit.

## For Claude agents working from a laptop

- Pushing to GitHub from a sandboxed shell corrupted the pack (`inflate: data stream error`). Push with the sandbox
  disabled.
- Commits should be attributed to the human (`git config user.name/user.email` per checkout).
