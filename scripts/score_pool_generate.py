"""Step 4a -- sample Qwen2.5-3B-Instruct k=8 times on every unique MATH prompt of the pool.

One SLURM array task per shard (launch/score_pool.sh). Resumable: finished chunks are skipped.

    $PY scripts/score_pool_generate.py --shard 3 --num-shards 16

Settings match the eval (same system prompt, chat template, temperature 0.6, top-p 0.95) except
max_tokens: 8192 instead of 32768, to keep the pass affordable. The base model rarely writes more than
~2K tokens; any sample that hits the cap is recorded (`finish`=="length") and counts as a failure.

Output: work/scores/gen/shard{S}_chunk{C}.parquet
    prompt_hash, rep_pool_idx, answers[8], gen_tokens[8], finish[8], (texts[8] with --save-text)
"""
import argparse
import os

import pandas as pd

from common import ANALYSIS, BASE_MODEL, EVAL_SYSTEM, WORK, import_eval_grader, load_pool, user_prompt

OUT = WORK / "scores" / "gen"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=int(os.environ.get("SLURM_ARRAY_TASK_ID", -1)))
    ap.add_argument("--num-shards", type=int, required=True)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--chunk", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--domains", nargs="+", default=["math"])
    ap.add_argument("--save-text", action="store_true")
    ap.add_argument("--gpu-mem", type=float, default=0.90)
    args = ap.parse_args()
    assert 0 <= args.shard < args.num_shards, "pass --shard or run as a SLURM array task"

    audit =pd.read_parquet(ANALYSIS / "pool_audit.parquet", columns=["pool_idx", "domain", "prompt_hash"])
    todo = (audit[audit.domain.isin(args.domains)].sort_values("pool_idx")
            .drop_duplicates("prompt_hash").sort_values("prompt_hash"))
    todo = todo.iloc[args.shard::args.num_shards]
    print(f"shard {args.shard}/{args.num_shards}: {len(todo)} unique prompts")

    pool = load_pool(["pool_idx", "instruction", "input"]).set_index("pool_idx")
    OUT.mkdir(parents=True, exist_ok=True)
    chunks = [todo.iloc[s:s + args.chunk] for s in range(0, len(todo), args.chunk)]
    pending = [(c, ch) for c, ch in enumerate(chunks)
               if not (OUT / f"shard{args.shard:03d}_chunk{c:03d}.parquet").exists()]
    if not pending:
        print("all chunks done")
        return

    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    extract_answer, _, _ = import_eval_grader()
    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    llm = LLM(model=BASE_MODEL, gpu_memory_utilization=args.gpu_mem, max_model_len=args.max_tokens + 4096,
              seed=args.seed, enable_prefix_caching=True)
    sp = SamplingParams(n=args.k, temperature=0.6, top_p=0.95, max_tokens=args.max_tokens, seed=args.seed)

    for c, ch in pending:
        prompts, keep = [], []
        for pid, ph in zip(ch.pool_idx, ch.prompt_hash):
            r = pool.loc[pid]
            # Same construction as eval.py: question.strip(), system + user via the chat template.
            text = tok.apply_chat_template(
                [{"role": "system", "content": EVAL_SYSTEM},
                 {"role": "user", "content": user_prompt(r.instruction, r.input).strip()}],
                tokenize=False, add_generation_prompt=True)
            if len(tok(text)["input_ids"]) > 4000:
                continue  # absurdly long prompt; leave unscored (pass_rate NaN)
            prompts.append(text)
            keep.append((pid, ph))
        outs = llm.generate(prompts, sp)
        rows = []
        for (pid, ph), o in zip(keep, outs):
            texts = [x.text for x in o.outputs]
            row = {"prompt_hash": ph, "rep_pool_idx": int(pid),
                   "answers": [extract_answer(t, "math") for t in texts],
                   "gen_tokens": [len(x.token_ids) for x in o.outputs],
                   "finish": [x.finish_reason for x in o.outputs]}
            if args.save_text:
                row["texts"] = texts
            rows.append(row)
        path = OUT / f"shard{args.shard:03d}_chunk{c:03d}.parquet"
        pd.DataFrame(rows).to_parquet(path.with_suffix(".tmp"), compression="zstd")
        path.with_suffix(".tmp").rename(path)
        print(f"chunk {c}: {len(rows)} prompts -> {path.name}", flush=True)


if __name__ == "__main__":
    main()
