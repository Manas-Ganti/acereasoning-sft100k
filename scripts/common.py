"""Paths, constants and helpers shared by every script.

The pool is identified by `pool_idx` = row position in the concatenated parquet shards of
`redsgnaoh/acereason11_100k` (sorted by shard name). `src_index` (extra_info.index) is the
upstream AceReason id and is kept as a secondary key.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# Large, gitignored artefacts. NOT $WORK: ARC defines WORK for every user (=/notavailable when no
# work filesystem is allocated), which silently redirected downloads there.
WORK = Path(os.environ.get("SFT_WORK_DIR", REPO / "work"))
EVAL_DIR = REPO / "eval"
ANALYSIS = REPO / "analysis"
SUBSETS = REPO / "data_subsets"
DEV_DIR = REPO / "dev"
RESULTS = REPO / "results"

POOL_REPO = "redsgnaoh/acereason11_100k"
POOL_FILE = "data/acereason11_100k.json"           # README 1.5: the file to download
POOL_JSON = WORK / "pool" / POOL_FILE              # hf_hub_download(local_dir=WORK/pool)
POOL_PARQUET = WORK / "pool" / "pool.parquet"      # same rows, same order; a faster cache
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"

# README sections 3-4: subsets live in LLaMA-Factory/data, checkpoints in saves/qwen25_3b_instruct.
LF_DIR = REPO / "LLaMA-Factory"
LF_DATA = LF_DIR / "data"
SAVES = LF_DIR / "saves" / "qwen25_3b_instruct"

# The eval system prompt (eval/prompts/qwen-instruct/*.py); every pool row carries it in `system`.
# NOTE: per the README registration ({"file_name": ...} only), LLaMA-Factory does not read the
# `system` column and trains with the qwen template's default system prompt. Decided 2026-10-05
# to follow the README literally.
EVAL_SYSTEM = "Please reason step by step, and put your final answer within \\boxed{}."
CUTOFF_LEN = 16384
SUBSET_SIZE = 15000

BENCHMARKS = ["aime", "math", "cn_math_2024", "kaoyan", "amc", "minerva", "olympiadbench", "gpqa"]
# Leaderboard AVG = AIME25, CN_MATH_24, KAOYAN, AMC, MINERVA, OLYMPIADBENCH, GPQA.
# AIME25 is not in eval/data, so locally we can only average the other six.
LB_VISIBLE = ["cn_math_2024", "kaoyan", "amc", "minerva", "olympiadbench", "gpqa"]
# Fall 2025 BASELINE row (Qwen2.5-3B-Instruct). These leaderboard numbers are Acc = pass@8 (any of 8
# samples correct), NOT Pass@1 -- verified on our AIME base run (Acc 0.167 vs 0.200; Pass@1 0.067).
BASELINE_REF = {"aime": 0.200, "math": 0.844, "cn_math_2024": 0.233, "kaoyan": 0.513,
                "amc": 0.700, "minerva": 0.338, "olympiadbench": 0.495, "gpqa": 0.742}
BASELINE_REF_LB_AVG = 0.446  # includes AIME25 = 0.100
# Fall 2025 random-15K runs (leaderboard AVG, pass@8) -- the published seed spread.
RANDOM_REF_LB_AVG = {"rand1": 0.451, "rand2": 0.492}


def import_eval_grader():
    """Return (extract_answer, check_is_correct, strip_string) from the frozen eval/ code."""
    if str(EVAL_DIR) not in sys.path:
        sys.path.insert(0, str(EVAL_DIR))
    from utils.parser import extract_answer, strip_string  # noqa: E402
    from utils.grader import check_is_correct  # noqa: E402
    return extract_answer, check_is_correct, strip_string


def safe_check(pred: str, gt: str) -> bool:
    """eval's check_is_correct, with a cheap exact-match fast path.

    check_is_correct spawns a process per symbolic comparison (3 s timeout); calling it from a
    daemonic worker raises, so fall back to the no-timeout path in that case.
    """
    _, check_is_correct, strip_string = import_eval_grader()
    if pred is None or gt is None or pred == "" or gt == "":
        return False
    try:
        if strip_string(pred) == strip_string(gt):
            return True
        return bool(check_is_correct(pred, gt))
    except AssertionError:  # "daemonic processes are not allowed to have children"
        try:
            return bool(check_is_correct(pred, gt, timeout=False))
        except Exception:
            return False
    except Exception:
        return False


def user_prompt(instruction: str, inp: str | None) -> str:
    """User turn exactly as LLaMA-Factory builds it from alpaca columns (instruction\\ninput)."""
    return instruction if not inp else f"{instruction}\n{inp}"


def normalize_prompt(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def prompt_hash(text: str) -> str:
    return hashlib.sha1(normalize_prompt(text).encode("utf-8")).hexdigest()[:16]


_TOKEN_RE = re.compile(r"[a-z0-9]+|[一-鿿]")


def ngram_tokens(text: str) -> list[str]:
    """Words for Latin text, single characters for CJK -- so kaoyan (Chinese) is comparable."""
    return _TOKEN_RE.findall(normalize_prompt(text))


def md_table(df, floatfmt: str = "{:.3f}") -> str:
    """Markdown table without the `tabulate` dependency."""
    cols = [str(c) for c in df.columns]
    fmt = lambda v: floatfmt.format(v) if isinstance(v, float) else str(v)  # noqa: E731
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def load_pool(columns: list[str] | None = None):
    import pandas as pd
    if not POOL_PARQUET.exists():
        raise SystemExit(f"{POOL_PARQUET} missing -- run scripts/fetch_data.py first")
    return pd.read_parquet(POOL_PARQUET, columns=columns)


def load_eval_questions() -> list[dict]:
    """All 8 test-benchmark questions, parsed the same way eval.py does."""
    out = []
    for bench in BENCHMARKS:
        with open(EVAL_DIR / "data" / bench / "test.jsonl", encoding="utf-8") as f:
            for i, line in enumerate(f):
                ex = json.loads(line)
                q = next((ex[k] for k in ["question", "problem", "Question", "input"] if k in ex), "")
                out.append({"bench": bench, "i": i, "question": q.strip()})
    return out


def load_dev_questions() -> list[dict]:
    out = []
    for p in sorted((DEV_DIR / "data").glob("*/test.jsonl")):
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f):
                ex = json.loads(line)
                out.append({"bench": "dev:" + p.parent.name, "i": i, "question": ex["question"]})
    return out


def write_subset(name: str, pool_idx: list[int], meta: dict) -> Path:
    """README section 3: write LLaMA-Factory/data/<name>.json and register it.

    Records carry exactly the README's four fields (instruction, input, output, system), copied
    unchanged from the pool. Provenance goes to data_subsets/<name>.meta.json and .idx.txt;
    data_subsets/<name>.json is a symlink to the training file.
    """
    import pandas as pd  # noqa: F401
    pool_idx = [int(i) for i in pool_idx]
    if len(pool_idx) != SUBSET_SIZE or len(set(pool_idx)) != SUBSET_SIZE:
        raise SystemExit(f"{name}: need exactly {SUBSET_SIZE} distinct rows, got "
                         f"{len(pool_idx)} ({len(set(pool_idx))} distinct)")
    pool = load_pool(["pool_idx", "instruction", "input", "output", "system"]).set_index("pool_idx")
    rows = pool.loc[pool_idx]
    records = [{"instruction": r.instruction, "input": r.input, "output": r.output, "system": r.system}
               for r in rows.itertuples()]
    LF_DATA.mkdir(parents=True, exist_ok=True)
    path = LF_DATA / f"{name}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)
    SUBSETS.mkdir(parents=True, exist_ok=True)
    link = SUBSETS / f"{name}.json"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(Path("..") / "LLaMA-Factory" / "data" / f"{name}.json")
    digest = hashlib.sha256(",".join(map(str, sorted(pool_idx))).encode()).hexdigest()
    meta = {"name": name, "n": len(records), "pool_idx_sha256": digest,
            "rows_with_system_not_eval_prompt": int((rows["system"] != EVAL_SYSTEM).sum()), **meta}
    (SUBSETS / f"{name}.meta.json").write_text(json.dumps(meta, indent=2, default=str))
    (SUBSETS / f"{name}.idx.txt").write_text("\n".join(map(str, pool_idx)) + "\n")
    register_dataset(name)
    print(f"wrote {path} ({len(records)} rows); meta -> data_subsets/{name}.meta.json")
    return path


def register_dataset(name: str) -> None:
    """README section 3: add {"<name>": {"file_name": "<name>.json"}} to LLaMA-Factory/data/dataset_info.json."""
    info_path = LF_DATA / "dataset_info.json"
    info = json.loads(info_path.read_text(encoding="utf-8"))
    info[name] = {"file_name": f"{name}.json"}
    info_path.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
