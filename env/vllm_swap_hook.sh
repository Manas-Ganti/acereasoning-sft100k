#!/bin/bash
# Raise vLLM's DEFAULT CPU swap space in evalenv (eval.py never passes swap_space; its `swap_space=60` is commented out).
#
# Why: trained models write long R1-style traces. With n=8 samples per prompt, vLLM preempts sequence groups by
# swapping their KV cache to CPU, and the 4 GiB/GPU default runs out:
#   RuntimeError: Aborted due to the lack of CPU swap space. Please increase the swap space to avoid this error.
# Seen on base OlympiadBench (1x A100, 2026-10-09) and on random_s1 gpqa (2x A100, 2026-10-15, at 94/198).
# This changes memory only -- sampling, prompts and grading are untouched, and eval/ is not modified (same reasoning
# as score_pool_generate.py's swap_space=32, decision log 2026-10-09).
#
# How: the default of LLM.__init__(swap_space=4) in vllm/entrypoints/llm.py is made to read VLLM_EVAL_SWAP_GB
# (default 4 if unset), and an evalenv activate.d hook sets VLLM_EVAL_SWAP_GB. eval_single.sh does `source activate`,
# so already-queued jobs pick it up. Batch eval jobs ask for --mem=96G: 2 GPUs x 24 GiB = 48 GiB of pinned swap.
#   bash env/vllm_swap_hook.sh [env prefix] [GiB per GPU]       # idempotent; backup llm.py.orig
set -euo pipefail
ENV_PREFIX="${1:-$HOME/.conda/envs/evalenv}"
GB="${2:-24}"
PY="$ENV_PREFIX/bin/python"
[ -x "$PY" ] || { echo "no env at $ENV_PREFIX"; exit 1; }
PYTHONNOUSERSITE=1 "$PY" - <<'EOF'
import pathlib, re, shutil, sys, vllm
p = pathlib.Path(vllm.__file__).parent / "entrypoints" / "llm.py"
src = p.read_text()
if "VLLM_EVAL_SWAP_GB" in src:
    print(f"already patched: {p}"); sys.exit(0)
pat = re.compile(r"(\bswap_space\s*:\s*(?:float|int)\s*=\s*)4\b")
hits = pat.findall(src)
if len(hits) != 1:
    lines = [l for l in src.splitlines() if "swap_space" in l]
    sys.exit(f"expected exactly one 'swap_space: float = 4' in {p}, found {len(hits)}:\n" + "\n".join(lines))
shutil.copy2(p, p.with_suffix(".py.orig"))
p.write_text(pat.sub(r'\1float(__import__("os").environ.get("VLLM_EVAL_SWAP_GB", 4))', src))
print(f"patched {p} (backup {p.name}.orig)")
EOF
mkdir -p "$ENV_PREFIX/etc/conda/activate.d"
echo "export VLLM_EVAL_SWAP_GB=$GB" > "$ENV_PREFIX/etc/conda/activate.d/vllm_swap.sh"
VLLM_EVAL_SWAP_GB="$GB" PYTHONNOUSERSITE=1 "$PY" -c "
import inspect, vllm
d = inspect.signature(vllm.LLM.__init__).parameters['swap_space'].default
assert d == $GB, d
print('vllm LLM default swap_space =', d, 'GiB per GPU')"
