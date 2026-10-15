"""Smoke-test a trained model in evalenv BEFORE its real evals run (~10 min on 1-2 GPUs).

    # inside a GPU allocation (srun ... --gres=gpu:a100:2), from the repo root:
    ~/.conda/envs/evalenv/bin/python scripts/smoke_eval.py random_s2

Loads the model the way eval/eval.py does -- AutoTokenizer + apply_chat_template with the eval system
prompt, then vLLM with tensor_parallel_size = number of visible GPUs -- and generates 2 samples for 2 AMC
questions. Fails loudly on anything that would sink a real eval:
  * tokenizer / chat template not loadable by evalenv's transformers (fix: scripts/fix_tokenizer_for_eval.py)
  * vLLM 0.6.1 can't load the saved config/weights, or tensor parallel / NCCL fails on this node
  * the model never stops (EOS mismatch -> every sample runs to max_tokens: an eval that takes days)
  * no \\boxed{} answer, so the grader would score everything wrong
eval/ is only read, never modified.
"""
import argparse
import json
import os
import sys
import time

from common import EVAL_DIR, EVAL_SYSTEM, SAVES


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--max-tokens", type=int, default=8192)
    args = ap.parse_args()
    model = SAVES / args.run
    if not (model / "DONE").exists():
        sys.exit(f"{model} has no DONE marker")
    gpus = os.environ.get("CUDA_VISIBLE_DEVICES", "0").split(",")
    print(f"[smoke] model={model} gpus={gpus}", flush=True)

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(model), trust_remote_code=True)
    rows = [json.loads(l) for l in open(EVAL_DIR / "data" / "amc" / "test.jsonl", encoding="utf-8")][:2]
    q = lambda r: next(r[k] for k in ["question", "problem", "Question", "input"] if k in r).strip()  # noqa: E731
    prompts = [tok.apply_chat_template([{"role": "system", "content": EVAL_SYSTEM}, {"role": "user", "content": q(r)}],
                                       tokenize=False, add_generation_prompt=True) for r in rows]
    print("[smoke] prompt 0 as eval builds it:\n" + prompts[0], flush=True)
    assert EVAL_SYSTEM in prompts[0], "chat template dropped the eval system prompt"
    print(f"[smoke] eos_token={tok.eos_token!r}", flush=True)

    from vllm import LLM, SamplingParams
    t = time.time()
    llm = LLM(model=str(model), tensor_parallel_size=len(gpus), trust_remote_code=True, gpu_memory_utilization=0.90)
    print(f"[smoke] vLLM loaded in {time.time() - t:.0f}s (tensor_parallel_size={len(gpus)})", flush=True)
    outs = llm.generate(prompts, SamplingParams(n=2, temperature=0.6, top_p=0.95, max_tokens=args.max_tokens, seed=0))

    problems = []
    for i, o in enumerate(outs):
        for j, c in enumerate(o.outputs):
            boxed = "\\boxed" in c.text
            print(f"[smoke] q{i} s{j}: {len(c.token_ids)} tokens, finish={c.finish_reason}, boxed={boxed}; "
                  f"tail: {c.text[-160:]!r}", flush=True)
            if c.finish_reason != "stop":
                problems.append(f"q{i} s{j} hit max_tokens ({args.max_tokens}): EOS mismatch or runaway trace")
            if not boxed:
                problems.append(f"q{i} s{j} has no \\boxed{{}}")
    # One long or unboxed sample can be genuine; all of them failing is a pipeline problem.
    if len(problems) >= 3:
        sys.exit("[smoke] FAIL:\n  " + "\n  ".join(problems))
    print("[smoke] PASS" + (f" (warnings: {problems})" if problems else ""))


if __name__ == "__main__":
    main()
