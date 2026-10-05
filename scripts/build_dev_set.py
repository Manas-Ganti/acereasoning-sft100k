"""Build the held-out DEV set (never the 8 test benchmarks). Login node; needs the GPQA licence
accepted on HF and a token under $HF_HOME.

    python scripts/build_dev_set.py

dev/data/<set>/test.jsonl + dev/prompts/qwen-instruct/<set>.py (same prompt as eval), so that the
unmodified eval/eval.py can run on it (see slurm/dev_eval.slurm):

  aime2223     AIME 2022 + 2023 (60)          AI-MO/aimo-validation-aime
  hmmt25       HMMT Feb 2025 (30)             MathArena/hmmt_feb_2025
  math_l5      MATH *train* level 5 (200)     EleutherAI/hendrycks_math
  gpqa_main    GPQA main minus Diamond (200)  Idavidrein/gpqa  -- same MC format as eval/gpqa

Anything overlapping an eval/data question (8-gram, >=50%) is dropped.
"""
import json
import random

from datasets import load_dataset

from common import DEV_DIR, import_eval_grader, load_eval_questions, ngram_tokens

SEED = 0
GPQA_SUFFIX = ("\n\nPlease reason step-by-step and put your choice letter without any other text "
               "with \\boxed{} in the end.")
PROMPT_PY = ('system_prompt = "Please reason step by step, and put your final answer within \\\\boxed{}."\n\n'
             'few_shot_prompt = ""\n\nquestion_format = """{question}"""\n')


def eval_grams():
    grams = set()
    for q in load_eval_questions():
        t = ngram_tokens(q["question"])
        grams |= {tuple(t[i:i + 8]) for i in range(max(1, len(t) - 7))}
    return grams


def overlaps(text, grams):
    t = ngram_tokens(text)
    g = {tuple(t[i:i + 8]) for i in range(max(1, len(t) - 7))}
    return len(g & grams) / max(1, len(g)) >= 0.5


def aime2223():
    ds = load_dataset("AI-MO/aimo-validation-aime", split="train")
    return [{"question": r["problem"], "answer": str(r["answer"]), "url": r["url"]}
            for r in ds if ("2022" in r["url"] or "2023" in r["url"])]


def hmmt25():
    ds = load_dataset("MathArena/hmmt_feb_2025", split="train")
    return [{"question": r["problem"], "answer": str(r["answer"])} for r in ds]


def math_l5(n=200):
    extract_answer, _, _ = import_eval_grader()
    rows = []
    for cfg in ["algebra", "counting_and_probability", "geometry", "intermediate_algebra",
                "number_theory", "prealgebra", "precalculus"]:
        for r in load_dataset("EleutherAI/hendrycks_math", cfg, split="train"):
            if r["level"] == "Level 5":
                ans = extract_answer(r["solution"], "math")
                if ans:
                    rows.append({"question": r["problem"], "answer": ans, "type": r["type"]})
    random.Random(SEED).shuffle(rows)
    return rows[:n]


def gpqa_main(n=200):
    diamond = {r["Question"].strip() for r in load_dataset("Idavidrein/gpqa", "gpqa_diamond", split="train")}
    rng = random.Random(SEED)
    rows = []
    for r in load_dataset("Idavidrein/gpqa", "gpqa_main", split="train"):
        if r["Question"].strip() in diamond:
            continue
        opts = [r["Correct Answer"], r["Incorrect Answer 1"], r["Incorrect Answer 2"], r["Incorrect Answer 3"]]
        opts = [o.strip() for o in opts]
        order = list(range(4))
        rng.shuffle(order)
        letters = "ABCD"
        body = "\n".join(f"{letters[i]}. {opts[j]}" for i, j in enumerate(order))
        rows.append({"question": f"{r['Question'].strip()}\n\n\n{body}{GPQA_SUFFIX}",
                     "answer": letters[order.index(0)]})
    rng.shuffle(rows)
    return rows[:n]


def main():
    grams = eval_grams()
    built = {}
    for name, fn in [("aime2223", aime2223), ("hmmt25", hmmt25), ("math_l5", math_l5), ("gpqa_main", gpqa_main)]:
        try:
            rows = fn()
        except Exception as e:  # dataset moved / gated -- report and continue
            print(f"[skip] {name}: {type(e).__name__}: {e}")
            continue
        kept = [r for r in rows if not overlaps(r["question"], grams)]
        d = DEV_DIR / "data" / name
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "test.jsonl", "w", encoding="utf-8") as f:
            for i, r in enumerate(kept):
                f.write(json.dumps({"id": i, **r}, ensure_ascii=False) + "\n")
        p = DEV_DIR / "prompts" / "qwen-instruct"
        p.mkdir(parents=True, exist_ok=True)
        (p / f"{name}.py").write_text(PROMPT_PY)
        built[name] = (len(rows), len(kept))
        print(f"{name}: {len(kept)} kept ({len(rows) - len(kept)} dropped for eval overlap)")
    (DEV_DIR / "manifest.json").write_text(json.dumps(
        {k: {"candidates": a, "kept": b} for k, (a, b) in built.items()}, indent=2))


if __name__ == "__main__":
    main()
