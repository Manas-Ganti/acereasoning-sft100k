#!/bin/bash
# Make vLLM preempt by SWAP only (never RECOMPUTE) in evalenv. eval.py never sets preemption_mode.
#
# Why: random_s2 math, olympiadbench and gpqa (2x A100, 2026-10-16/17) died after 1.3-2 h with
#   vllm/core/scheduler.py, in schedule:  assert len(seqs) == 1   AssertionError
# vLLM 0.6.1 bug with n>1: when a group of 8 samples is down to one running sequence (the others finished), the default
# policy preempts it by RECOMPUTE. The group comes back as a "prefill", and schedule() asserts a prefill holds exactly
# one sequence, but get_seqs() still returns all 8 (finished ones included). Trained models write long traces, so the
# KV cache fills, preemption happens, and long benchmarks hit it. Forcing SWAP never takes that path. The swap space is
# 24 GiB/GPU (env/vllm_swap_hook.sh). This changes scheduling/memory only: sampling, prompts and grading are untouched,
# and eval/ is not modified (same reasoning as the swap and spawn hooks, decision log 2026-10-15).
#
# How: the EngineArgs default `preemption_mode: Optional[str] = None` in vllm/engine/arg_utils.py is made to read
# VLLM_EVAL_PREEMPTION_MODE (None if unset = vLLM's own behaviour), and an evalenv activate.d hook sets it to "swap".
# eval_single.sh does `source activate`, so already-queued jobs pick it up.
#   bash env/vllm_preempt_hook.sh [env prefix]       # idempotent; backup arg_utils.py.orig
set -euo pipefail
ENV_PREFIX="${1:-$HOME/.conda/envs/evalenv}"
PY="$ENV_PREFIX/bin/python"
[ -x "$PY" ] || { echo "no env at $ENV_PREFIX"; exit 1; }
PYTHONNOUSERSITE=1 "$PY" - <<'EOF'
import pathlib, re, shutil, sys, vllm
root = pathlib.Path(vllm.__file__).parent
sched = (root / "core" / "scheduler.py").read_text()
# the policy we rely on: a user-specified "swap" always swaps
if 'user_specified_preemption_mode == "swap"' not in sched:
    sys.exit("scheduler.py has no 'user_specified_preemption_mode == \"swap\"' branch -- vLLM version differs, not patching")
p = root / "engine" / "arg_utils.py"
src = p.read_text()
if "preemption_mode=self.preemption_mode" not in src:
    sys.exit(f"{p} does not pass preemption_mode=self.preemption_mode to SchedulerConfig -- not patching")
if "VLLM_EVAL_PREEMPTION_MODE" in src:
    print(f"already patched: {p}"); sys.exit(0)
pat = re.compile(r"(\bpreemption_mode\s*:\s*Optional\[str\]\s*=\s*)None\b")
hits = pat.findall(src)
if len(hits) != 1:
    lines = [l for l in src.splitlines() if "preemption_mode" in l]
    sys.exit(f"expected exactly one 'preemption_mode: Optional[str] = None' in {p}, found {len(hits)}:\n" + "\n".join(lines))
shutil.copy2(p, p.with_suffix(".py.orig"))
p.write_text(pat.sub(r'\1(__import__("os").environ.get("VLLM_EVAL_PREEMPTION_MODE") or None)', src))
print(f"patched {p} (backup {p.name}.orig)")
EOF
mkdir -p "$ENV_PREFIX/etc/conda/activate.d"
echo "export VLLM_EVAL_PREEMPTION_MODE=swap" > "$ENV_PREFIX/etc/conda/activate.d/vllm_preempt.sh"
VLLM_EVAL_PREEMPTION_MODE=swap PYTHONNOUSERSITE=1 "$PY" -c "
from vllm.engine.arg_utils import EngineArgs
m = EngineArgs(model='x').preemption_mode
assert m == 'swap', m
print('vllm EngineArgs default preemption_mode =', m)"
