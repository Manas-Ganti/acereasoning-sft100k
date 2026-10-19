# Reasoning SFT data selection: Qwen2.5-3B-Instruct on a 15K subset of AceReason-1.1-SFT

ECE 6514 project. We fine-tune **Qwen/Qwen2.5-3B-Instruct** on 15K samples chosen from a fixed 100K pool of
AceReason-1.1-SFT (R1-distilled math and code), and ask: **does a smart 15K subset beat a random one, at identical
hyperparameters, by more than seed noise?**

This repo is a superset of the course repo [reds-lab/Project-Reasoning-SFT-LLM](https://github.com/reds-lab/Project-Reasoning-SFT-LLM)
(commit `4d31bfc`). `eval/` and `LLaMA-Factory/` are copied from it, and `eval/` is byte-identical. The course README's
steps are followed as written; every deviation is listed in
[docs/reference/upstream-compliance.md](docs/reference/upstream-compliance.md).

## Documentation

The project docs live in [`docs/`](docs/00-home.md), written so they read the same on GitHub and in **Obsidian**
(open the repo folder as a vault).

| | |
|---|---|
| [Home](docs/00-home.md) | overview, the seven steps, navigation |
| [**STATUS**](docs/STATUS.md) | **where the project is right now**: step board, running jobs, next actions |
| [Step notes 0–7](docs/00-home.md) | one note per step: goal, commands, gate, results |
| [Decision log](docs/reference/decision-log.md) | every deliberate choice, dated |
| [ARC guide](docs/reference/arc-guide.md) | cluster setup and gotchas already solved |
| [Eval facts](docs/reference/eval-facts.md) · [Repo map](docs/reference/repo-map.md) | reference |
| [CLAUDE.md](CLAUDE.md) | the protocol and invariants (also the instructions for Claude agents) |

## Quick start (VT ARC)

```bash
git clone git@github.com:Manas-Ganti/acereasoning-sft100k.git && cd acereasoning-sft100k
bash env/setup_envs.sh && bash env/check_envs.sh       # myenv (training) + evalenv (eval)
PY=~/.conda/envs/evalenv/bin/python
$PY scripts/fetch_data.py && $PY scripts/build_dev_set.py
launch/cpu.sh python scripts/audit_pool.py             # Step 1
launch/eval_model.sh base                              # Step 2
```

Then follow [STATUS](docs/STATUS.md) and the step notes linked from [Home](docs/00-home.md).

## Results

Pass@8 with the course's fixed eval; AVG = mean of the six visible leaderboard benchmarks (CN-Math, Kaoyan, AMC,
Minerva, OlympiadBench, GPQA). Full write-up: [report/report.md](report/report.md).

| Model | AIME24 | MATH | CN-Math | Kaoyan | AMC | Minerva | Olympiad | GPQA | AVG |
|---|---|---|---|---|---|---|---|---|---|
| Base (Qwen2.5-3B-Instruct) | 0.167 | 0.854 | 0.400 | 0.528 | 0.650 | 0.489 | 0.492 | 0.707 | 0.544 |
| Random 15K | 0.233 | 0.848 | 0.367 | 0.608 | 0.700 | 0.452 | *TODO* | 0.768 | *TODO* |
| Advanced 15K | 0.133 | 0.872 | 0.367 | 0.603 | 0.700 | 0.474 | 0.505 | 0.798 | 0.575 |

**Hugging Face**

| | Model | Dataset |
|---|---|---|
| Random 15K | *TODO* | *TODO* |
| Advanced 15K | *TODO* | *TODO* |
