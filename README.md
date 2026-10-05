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

*(filled in at Step 7: see [results/results.md](results/results.md))*
