"""Step 4b -- grade the base-model samples against R1's boxed answer, compute R1 self-agreement,
and (re)build analysis/pool_scores.parquet. CPU job (uses the frozen eval grader).

    launch/cpu.sh python scripts/score_pool_grade.py --workers 32

pass_rate is per pool ROW, not per prompt: the same prompt can have several R1 responses with
different final answers, and each row is graded against its own R1 answer.

r1_agreement (per prompt with >1 R1 response) = size of the largest group of equivalent R1
answers / number of responses.  r1_in_majority (per row) = this row's answer is in that group.
Singletons get r1_agreement = NaN (no evidence either way).
"""
import argparse
import math
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from common import ANALYSIS, WORK, safe_check

GEN = WORK / "scores" / "gen"


def grade_chunk(items):
    """items: list of (pool_idx, r1_answer, [base answers]) -> list of (pool_idx, [bool])."""
    memo = {}  # the 8 samples often repeat an answer; symbolic checks cost ~0.1 CPU-s each

    def check(b, r1):
        if (b, r1) not in memo:
            memo[(b, r1)] = safe_check(b, r1)
        return memo[(b, r1)]
    return [(pid, [check(b, r1) for b in base]) for pid, r1, base in items]


def agree_chunk(groups):
    """groups: list of (prompt_hash, [(pool_idx, r1_answer)]) -> list of (pool_idx, agreement, in_majority)."""
    out = []
    for _, members in groups:
        n = len(members)
        parent = list(range(n))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(n):
            for j in range(i + 1, n):
                if find(i) != find(j) and safe_check(members[i][1], members[j][1]):
                    parent[find(i)] = find(j)
        roots = [find(i) for i in range(n)]
        sizes = pd.Series(roots).value_counts()
        best = int(sizes.iloc[0])
        for (pid, ans), r in zip(members, roots):
            # strict majority: this answer is shared by more than half of the R1 responses
            out.append((pid, best / n, bool(ans) and sizes[r] > n / 2))
    return out


def chunked(xs, n):
    size = max(1, math.ceil(len(xs) / n))
    return [xs[i:i + size] for i in range(0, len(xs), size)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=32)
    args = ap.parse_args()

    audit = pd.read_parquet(ANALYSIS / "pool_audit.parquet")
    files = sorted(GEN.glob("shard*_chunk*.parquet"))
    if not files:
        raise SystemExit(f"no generations in {GEN}")
    gen = pd.concat([pd.read_parquet(f, columns=["prompt_hash", "answers", "gen_tokens", "finish"]) for f in files])
    gen = gen.drop_duplicates("prompt_hash").set_index("prompt_hash")
    print(f"{len(gen)} scored prompts from {len(files)} files")

    rows = audit[audit.prompt_hash.isin(gen.index)][["pool_idx", "prompt_hash", "r1_answer"]]
    items = [(int(p), a, list(gen.at[h, "answers"])) for p, h, a in rows.itertuples(index=False)]
    print(f"grading {len(items)} rows x k ...")
    with ProcessPoolExecutor(args.workers) as ex:
        graded = [g for part in ex.map(grade_chunk, chunked(items, args.workers * 8)) for g in part]
    res = pd.DataFrame(graded, columns=["pool_idx", "correct"])
    res["k"] = res["correct"].map(len)
    res["n_correct"] = res["correct"].map(sum)
    res["pass_rate"] = res["n_correct"] / res["k"]
    res = res.drop(columns="correct")

    ph = rows.set_index("pool_idx")["prompt_hash"]
    res["base_mean_tokens"] = [float(np.mean(gen.at[ph[p], "gen_tokens"])) for p in res.pool_idx]
    res["base_cap_frac"] = [float(np.mean([f == "length" for f in gen.at[ph[p], "finish"]])) for p in res.pool_idx]

    multi = audit[audit.dup_count > 1]
    groups = [(h, list(zip(g.pool_idx.astype(int), g.r1_answer))) for h, g in multi.groupby("prompt_hash")]
    print(f"R1 agreement over {len(groups)} multi-response prompts ...")
    with ProcessPoolExecutor(args.workers) as ex:
        agr = [x for part in ex.map(agree_chunk, chunked(groups, args.workers * 8)) for x in part]
    agr = pd.DataFrame(agr, columns=["pool_idx", "r1_agreement", "r1_in_majority"])

    grades = (audit[["pool_idx"]].merge(res, on="pool_idx", how="left")
              .merge(agr, on="pool_idx", how="left"))
    grades.to_parquet(ANALYSIS / "pool_grades.parquet")
    print(grades[["pass_rate", "r1_agreement"]].describe().to_string())
    from build_pool_scores import build
    build()


if __name__ == "__main__":
    main()
