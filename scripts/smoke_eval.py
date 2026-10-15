"""Smoke-test a trained model in evalenv BEFORE its real evals run (~10 min on 1-2 GPUs).

    # inside a GPU allocation (srun ... --gres=gpu:a100:2), from the repo root:
    ~/.conda/envs/evalenv/bin/python scripts/smoke_eval.py random_s2
    # file checks only, seconds, login node, no GPU:
    ~/.conda/envs/evalenv/bin/python scripts/smoke_eval.py random_s2 --static-only

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

from common import BASE_MODEL, EVAL_DIR, EVAL_SYSTEM, SAVES

# config.json fields vLLM 0.6.1 relies on; SFT must not change any of them.
CONFIG_KEYS = ["architectures", "vocab_size", "hidden_size", "num_hidden_layers", "num_attention_heads",
               "num_key_value_heads", "max_position_embeddings", "rope_theta", "rope_scaling", "tie_word_embeddings"]


def static_checks(model):
    """Compare the saved model's config / generation_config / tokenizer_config with the base model's. No GPU."""
    from huggingface_hub import hf_hub_download
    load = lambda p: json.loads(open(p, encoding="utf-8").read())  # noqa: E731
    problems = []
    cfg, base_cfg = load(model / "config.json"), load(hf_hub_download(BASE_MODEL, "config.json"))
    for k in CONFIG_KEYS:
        if cfg.get(k) != base_cfg.get(k):
            problems.append(f"config.json {k}: trained={cfg.get(k)!r} base={base_cfg.get(k)!r}")
    # vLLM 0.6.1 reads `torch_dtype`; without it, dtype='auto' resolves to fp32 -> fp16 (Qwen2.5 can overflow).
    dtype = cfg.get("torch_dtype")
    print(f"[static] config torch_dtype={dtype!r} (dtype={cfg.get('dtype')!r})")
    if dtype != "bfloat16":
        problems.append(f"config.json torch_dtype={dtype!r}, expected 'bfloat16' (vLLM would pick another dtype)")
    # vLLM adds generation_config eos_token_id(s) as stop tokens: Qwen2.5-Instruct uses [151645, 151643].
    gpath = model / "generation_config.json"
    base_eos = load(hf_hub_download(BASE_MODEL, "generation_config.json")).get("eos_token_id")
    eos = load(gpath).get("eos_token_id") if gpath.exists() else None
    print(f"[static] generation_config eos_token_id={eos!r} (base {base_eos!r})")
    if not gpath.exists():
        problems.append("generation_config.json missing (copy the base model's)")
    elif 151645 not in (eos if isinstance(eos, list) else [eos]):
        problems.append(f"generation_config eos_token_id {eos!r} lacks 151645 (<|im_end|>): samples may never stop")
    tcfg = load(model / "tokenizer_config.json")
    print(f"[static] tokenizer_config eos_token={tcfg.get('eos_token')!r}, chat_template present={bool(tcfg.get('chat_template'))}")
    if tcfg.get("eos_token") != "<|im_end|>":
        problems.append(f"tokenizer_config eos_token={tcfg.get('eos_token')!r}, expected '<|im_end|>'")
    if not tcfg.get("chat_template"):
        problems.append("tokenizer_config has no chat_template: run scripts/fix_tokenizer_for_eval.py")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--static-only", action="store_true", help="file checks only (login node, no GPU)")
    args = ap.parse_args()
    model = SAVES / args.run
    if not (model / "DONE").exists():
        sys.exit(f"{model} has no DONE marker")
    problems = static_checks(model)
    if problems:
        sys.exit("[static] FAIL:\n  " + "\n  ".join(problems))
    print("[static] PASS: config, stop tokens, dtype and chat template match the base model")
    if args.static_only:
        return
    gpus = os.environ.get("CUDA_VISIBLE_DEVICES", "0").split(",")
    print(f"[smoke] model={model} gpus={gpus} NCCL_SOCKET_IFNAME={os.environ.get('NCCL_SOCKET_IFNAME', 'unset')} "
          f"host={os.uname().nodename}", flush=True)

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
