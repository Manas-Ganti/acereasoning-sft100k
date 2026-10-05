"""Step 1 -- audit the 100K pool (CPU only, ~10-20 min on 16 cores).

    launch/cpu.sh python scripts/audit_pool.py

Writes analysis/pool_audit.parquet (one row per pool sample, no text) and analysis/pool_audit.md.
Re-run after building dev/ so that `contam_dev` is filled in.

Columns
  domain              math / code / other            (from extra_info.category)
  prompt_tokens       chat-templated system+user prompt, Qwen2.5 tokenizer
  resp_tokens         response, Qwen2.5 tokenizer
  total_tokens        prompt + response + 2 (<|im_end|>\\n appended by the qwen template)
  truncated           total_tokens > 16384 (LLaMA-Factory cutoff_len would cut the tail)
  has_think_close     response contains </think>
  has_boxed           a balanced \\boxed{...} appears in the final solution (after </think>)
  r1_answer           eval/utils/parser.extract_answer(response)  -- the grader's view of R1's answer
  answer_kind         none / mc / numeric / expression / text
  proof_like          prompt asks for a proof, or the boxed answer is prose
  prompt_hash         normalized user prompt hash; dup_count = rows sharing it
  contam*             n-gram overlap with eval/data/*/test.jsonl questions (8-grams; CJK per char)
  flag_*              repetition loop / language mixing / malformed
"""
import os

os.environ["TOKENIZERS_PARALLELISM"] = "true"

import re  # noqa: E402
import zlib  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

from common import (ANALYSIS, BASE_MODEL, CUTOFF_LEN, EVAL_SYSTEM, import_eval_grader,  # noqa: E402
                    load_dev_questions, load_eval_questions, load_pool, md_table, ngram_tokens,
                    prompt_hash, user_prompt)

N_GRAM = 8
CONTAM_THRESHOLD = 0.5  # fraction of an eval question's 8-grams found in the pool prompt
CJK_RE = re.compile(r"[一-鿿]")
NUM_RE = re.compile(r"^-?\(?-?\d+(\.\d+)?\)?(\^\{?\d+\}?)?$|^-?\\?d?frac\{-?\d+\}\{\d+\}$|^-?\d+/\d+$")
PROOF_RE = re.compile(r"^\s*(\(\w\)\s*)?(prove|show that|demonstrate|verify that|证明)", re.I)


def tokenize_lengths(tok, texts, bs=256):
    out = np.zeros(len(texts), dtype=np.int32)
    for s in range(0, len(texts), bs):
        enc = tok(texts[s:s + bs], add_special_tokens=False)["input_ids"]
        out[s:s + bs] = [len(e) for e in enc]
        if s % (bs * 40) == 0:
            print(f"  tokenized {s}/{len(texts)}", flush=True)
    return out


def last_boxed_balanced(text: str) -> bool:
    i = text.rfind("\\boxed{")
    if i < 0:
        return False
    depth = 0
    for c in text[i + 6:]:
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return True
    return False


def answer_kind(ans: str, strip_string) -> str:
    if not ans:
        return "none"
    a = ans.strip()
    if re.fullmatch(r"\(?[A-E]\)?", a):
        return "mc"
    try:
        s = strip_string(a)
    except Exception:
        s = a
    if NUM_RE.match(s.replace(",", "")):
        return "numeric"
    words = re.findall(r"[A-Za-z]{3,}", re.sub(r"\\[A-Za-z]+", " ", a))
    if len(words) >= 3:
        return "text"
    return "expression"


def text_flags(out: str, prompt_has_cjk: bool):
    b = out.encode("utf-8", "ignore")
    tail = b[-4000:]
    tail_ratio = len(zlib.compress(tail)) / max(1, len(tail))
    lines = [ln.strip() for ln in out.split("\n") if len(ln.strip()) >= 30]
    max_line_repeat = max(Counter(lines).values()) if lines else 0
    cjk = len(CJK_RE.findall(out))
    n_open, n_close = out.count("<think>"), out.count("</think>")
    # A missing </think> (unfinished reasoning) is captured by has_think_close / has_boxed instead.
    # Short final sections (e.g. "\boxed{No}") are legitimate, so length is not a criterion.
    malformed = n_open != 1 or n_close > 1
    return {
        "tail_zlib_ratio": round(tail_ratio, 4),
        "max_line_repeat": max_line_repeat,
        "cjk_chars_resp": cjk,
        # Normal traces: tail ratio ~0.37 (min 0.19 on a 2K-row sample); lines like "Wait, let me
        # recheck." legitimately recur ~10x, so only a heavy repeat count counts as a loop.
        "flag_repetition": (len(tail) >= 2000 and tail_ratio < 0.10) or max_line_repeat >= 25,
        "flag_lang_mix": (not prompt_has_cjk) and cjk >= 20,
        "flag_malformed": malformed,
    }


def build_contam_index(questions):
    """8-gram -> list of question ids; drop 8-grams shared by >5 questions (boilerplate)."""
    index, sizes = defaultdict(list), []
    for qi, q in enumerate(questions):
        toks = ngram_tokens(q["question"])
        grams = {tuple(toks[j:j + N_GRAM]) for j in range(max(1, len(toks) - N_GRAM + 1))}
        sizes.append(len(grams))
        for g in grams:
            index[g].append(qi)
    index = {g: v for g, v in index.items() if len(v) <= 5}
    return index, sizes


def contam_scores(prompts, questions):
    index, sizes = build_contam_index(questions)
    best_score = np.zeros(len(prompts))
    best_q = np.full(len(prompts), -1)
    for pi, p in enumerate(prompts):
        toks = ngram_tokens(p)
        hits = Counter()
        for j in range(max(1, len(toks) - N_GRAM + 1)):
            for qi in index.get(tuple(toks[j:j + N_GRAM]), ()):
                hits[qi] += 1
        if hits:
            qi, c = max(hits.items(), key=lambda kv: kv[1] / sizes[kv[0]])
            best_score[pi], best_q[pi] = c / sizes[qi], qi
    return best_score, best_q


def main():
    extract_answer, _, strip_string = import_eval_grader()
    pool = load_pool()
    print(f"pool rows: {len(pool)}")
    users = [user_prompt(a, b) for a, b in zip(pool["instruction"], pool["input"])]

    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    templated = [tok.apply_chat_template([{"role": "system", "content": EVAL_SYSTEM},
                                          {"role": "user", "content": u}],
                                         tokenize=False, add_generation_prompt=True) for u in users]
    print("tokenizing prompts")
    prompt_tokens = tokenize_lengths(tok, templated)
    print("tokenizing responses")
    resp_tokens = tokenize_lengths(tok, pool["output"].tolist())

    a = pd.DataFrame({"pool_idx": pool["pool_idx"], "src_index": pool["src_index"],
                      "source": pool["source"]})
    a["domain"] = pool["category"].map(lambda c: c if c in ("math", "code") else "other")
    a["prompt_tokens"] = prompt_tokens
    a["resp_tokens"] = resp_tokens
    a["total_tokens"] = prompt_tokens + resp_tokens + 2
    a["truncated"] = a["total_tokens"] > CUTOFF_LEN
    a["system_ok"] = pool["system"] == EVAL_SYSTEM

    print("answers + flags")
    rows = []
    for u, out in zip(users, pool["output"]):
        post = out.split("</think>")[-1] if "</think>" in out else ""
        ans = extract_answer(out, "math") if "boxed" in out else ""
        kind = answer_kind(ans, strip_string)
        rows.append({
            "has_think_close": "</think>" in out,
            "has_boxed": bool(ans) and last_boxed_balanced(post),
            "r1_answer": ans[:500],
            "answer_kind": kind,
            "proof_like": bool(PROOF_RE.search(u[:300])) or kind == "text",
            **text_flags(out, bool(CJK_RE.search(u))),
        })
    a = pd.concat([a, pd.DataFrame(rows)], axis=1)
    a["flagged"] = a["flag_repetition"] | a["flag_lang_mix"] | a["flag_malformed"]

    a["prompt_hash"] = [prompt_hash(u) for u in users]
    a["dup_count"] = a.groupby("prompt_hash")["pool_idx"].transform("size")

    print("contamination vs eval/data")
    evq = load_eval_questions()
    score, qi = contam_scores(users, evq)
    a["contam_score"] = score.round(3)
    a["contam_bench"] = [evq[i]["bench"] if i >= 0 else "" for i in qi]
    a["contam_qid"] = qi
    a["contam"] = a["contam_score"] >= CONTAM_THRESHOLD
    devq = load_dev_questions()
    if devq:
        dscore, _ = contam_scores(users, devq)
        a["contam_dev"] = dscore >= CONTAM_THRESHOLD
    else:
        a["contam_dev"] = False
        print("  (dev/ not built yet -- contam_dev is all False; re-run after scripts/build_dev_set.py)")

    ANALYSIS.mkdir(exist_ok=True)
    a.to_parquet(ANALYSIS / "pool_audit.parquet", compression="zstd")
    write_report(a, users, evq, bool(devq))
    print(f"wrote {ANALYSIS / 'pool_audit.parquet'} and pool_audit.md")


def pct(x):
    return f"{100 * x:.1f}%"


def write_report(a, users, evq, have_dev):
    L = ["# Pool audit (100K AceReason-1.1-SFT subset)", "",
         f"Tokenizer: Qwen2.5-3B-Instruct. Truncation = prompt+response > {CUTOFF_LEN} (training cutoff_len). "
         f"Contamination = >= {CONTAM_THRESHOLD:.0%} of an eval question's {N_GRAM}-grams present in the pool prompt.", ""]

    g = a.groupby("domain")
    t = pd.DataFrame({
        "n": g.size(),
        "unique prompts": g["prompt_hash"].nunique(),
        "resp p50": g["resp_tokens"].median().astype(int),
        "resp p90": g["resp_tokens"].quantile(0.9).astype(int),
        "resp p99": g["resp_tokens"].quantile(0.99).astype(int),
        "resp max": g["resp_tokens"].max(),
        "truncated": g["truncated"].mean().map(pct),
        "no </think>": (1 - g["has_think_close"].mean()).map(pct),
        "has_boxed": g["has_boxed"].mean().map(pct),
        "flagged": g["flagged"].mean().map(pct),
        "contam": g["contam"].sum(),
    }).reset_index()
    L += ["## By domain", "", md_table(t), ""]

    s = a.groupby(["domain", "source"]).size().reset_index(name="n").sort_values("n", ascending=False)
    L += ["## By source", "", md_table(s), ""]

    m = a[a.domain == "math"]
    k = m["answer_kind"].value_counts().reset_index()
    k.columns = ["answer_kind", "n"]
    L += ["## Math: answer kinds (R1's last \\boxed{})", "", md_table(k), "",
          f"proof_like: {m['proof_like'].sum()} ({pct(m['proof_like'].mean())}). "
          "`text` answers (e.g. `\\boxed{\\text{The pentagon is regular.}}`) cannot be graded and give no pass-rate signal.", ""]

    f = pd.DataFrame({"flag": ["flag_repetition", "flag_lang_mix", "flag_malformed", "truncated"],
                      "math": [int(m[c].sum()) for c in ["flag_repetition", "flag_lang_mix", "flag_malformed", "truncated"]],
                      "all": [int(a[c].sum()) for c in ["flag_repetition", "flag_lang_mix", "flag_malformed", "truncated"]]})
    L += ["## Quality flags", "", md_table(f), ""]

    d = a.drop_duplicates("prompt_hash")["dup_count"].value_counts().sort_index().reset_index()
    d.columns = ["responses per prompt", "prompts"]
    L += ["## Duplicate prompts (multiple R1 responses)", "", md_table(d), ""]

    clean = m[~m.truncated & m.has_boxed & ~m.contam & ~m.flagged]
    L += ["## Math rows surviving the basic filter", "",
          f"not truncated & has_boxed & not contam & not flagged: **{len(clean)}** rows, "
          f"{clean['prompt_hash'].nunique()} unique prompts; excluding proof_like: "
          f"{int((~clean.proof_like).sum())} rows.", ""]

    c = a[a.contam].sort_values("contam_score", ascending=False)
    L += [f"## Contamination: {len(c)} pool rows match an eval question", ""]
    if len(c):
        cb = c.groupby("contam_bench").agg(rows=("pool_idx", "size"), eval_questions=("contam_qid", "nunique")).reset_index()
        L += [md_table(cb), "", "Top matches:", ""]
        for _, r in c.head(8).iterrows():
            L.append(f"- `{r.contam_bench}` score {r.contam_score:.2f} -- pool: "
                     f"{users[int(r.pool_idx)][:110]!r} / eval: {evq[int(r.contam_qid)]['question'][:110]!r}")
        L.append("")
    if have_dev:
        L += [f"Dev-set overlap (contam_dev): {int(a.contam_dev.sum())} rows.", ""]
    (ANALYSIS / "pool_audit.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()
