"""Third smart selection (added 2026-10-20): medium difficulty, short traces -> short_mid_s<seed>.

    python scripts/select_short_mid.py --seed 1 --dry-run     # funnel + composition, writes nothing
    python scripts/select_short_mid.py --seed 1               # -> short_mid_s1

Hypothesis: a 3B model learns little from R1 traces on problems it never solves (71% of full_method_s1 is
pass_rate 0) and copies R1's length without its ability to finish. So: train on problems Qwen-3B *sometimes*
solves, with R1's *shorter* traces. Against medium_s1 (same band + topic balance, no length cap, built by Manas
2026-10-20) this run isolates the length cap.

Procedure, deterministic:
  1. The same quality filter as every select_subset.py preset: math only; drop truncated, no balanced
     \\boxed{}, proof-like / prose answer, contaminated (test AND dev), flagged.
  2. The same label-noise rule as the difficulty presets: drop pass_rate-0 rows whose R1 answer is not
     the R1 majority.
  3. Length cap: resp_tokens <= 8192 (Qwen2.5 tokens), the same cap Step 4 scored pass_rate with.
  4. Tier per row: 0 = pass_rate in [0.25, 0.75] (primary), 1 = pass_rate 0 (fill), 2 = pass_rate 1.0 (fill).
  5. One response per prompt: best tier, then majority-agreeing, then the SHORTEST, then lowest pool_idx.
  6. Tiers are taken in order, each sampled with select_subset's cluster water-filling (seed), until 15,000.
Reuses common.write_subset, so the outputs are exactly what select_subset.py writes, and subset_from_idx.py /
make_config.py / launch/train.sh work unchanged. Fewer training tokens than random: the report states the ratio.
"""
import argparse
import json

import numpy as np
import pandas as pd

from common import ANALYSIS, SUBSET_SIZE, write_subset
from select_subset import sample

METHOD = "short_mid"
MAX_RESP_TOKENS = 8192
BAND = (0.25, 0.75)
TIER_LABELS = {0: f"pass_rate in [{BAND[0]}, {BAND[1]}]", 1: "fill: pass_rate 0", 2: "fill: pass_rate 1.0"}
REF_TOKENS = 112e6  # full_method_s1 sum_total_tokens (~112M); random is similar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--name", default=None, help="override output name (default short_mid_s<seed>)")
    ap.add_argument("--max-resp-tokens", type=int, default=MAX_RESP_TOKENS)
    ap.add_argument("--scores", default=str(ANALYSIS / "pool_scores.parquet"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    name = args.name or f"{METHOD}_s{args.seed}"
    rng = np.random.default_rng(args.seed)

    df = pd.read_parquet(args.scores)
    funnel = [("pool", len(df))]

    def keep(mask, label):
        nonlocal df
        df = df[mask]
        funnel.append((label, len(df)))

    keep(df.domain == "math", "math")
    keep(~df.truncated, "not truncated (<=16384 tokens)")
    keep(df.has_boxed & (df.answer_kind != "none"), "balanced \\boxed{} in final answer")
    keep(~df.proof_like, "not proof-like / prose answer")
    keep(~df.contam, "not contaminated (test)")
    keep(~df.contam_dev, "not contaminated (dev)")
    keep(~df.flagged, "no repetition / lang-mix / malformed flag")
    if "pass_rate" not in df or "cluster_id" not in df:
        raise SystemExit("pool_scores.parquet needs pass_rate and cluster_id -- run Step 4 first")
    keep(df.pass_rate.notna(), "scored")
    noisy = (df.pass_rate == 0) & df.r1_agreement.notna() & ~df.r1_in_majority.fillna(False).astype(bool)
    keep(~noisy, "drop pass_rate-0 rows whose R1 answer is not the R1 majority")
    keep(df.resp_tokens <= args.max_resp_tokens, f"resp_tokens <= {args.max_resp_tokens}")

    tier = np.select([df.pass_rate.between(BAND[0] - 1e-9, BAND[1] + 1e-9), df.pass_rate == 0, df.pass_rate == 1],
                     [0, 1, 2], default=-1)
    df = df.assign(_tier=tier, _pref=df.r1_in_majority.fillna(True).astype(bool))
    keep(df._tier >= 0, "in band or a fill tier")

    # One response per prompt: best tier, majority-agreeing, shortest, lowest pool_idx.
    df = df.sort_values(["prompt_hash", "_tier", "_pref", "resp_tokens", "pool_idx"],
                        ascending=[True, True, False, True, True])
    primary = df.drop_duplicates("prompt_hash").sort_values("pool_idx")
    funnel.append(("unique prompts (1 response each)", len(primary)))
    avail = primary._tier.value_counts().to_dict()

    parts, taken = [], {}
    for t in (0, 1, 2):
        need = SUBSET_SIZE - sum(len(p) for p in parts)
        if need <= 0:
            break
        got = sample(primary[primary._tier == t], need, rng, stratify=True)
        parts.append(got)
        taken[t] = len(got)
    chosen = pd.concat(parts)
    for t, n in taken.items():
        funnel.append((f"selected from {TIER_LABELS[t]} (of {avail.get(t, 0)})", n))
    funnel.append(("selected", len(chosen)))

    print(f"\n{name}  (method={METHOD}, band={BAND}, max_resp_tokens={args.max_resp_tokens})")
    for label, n in funnel:
        print(f"  {n:>7}  {label}")
    if len(chosen) < SUBSET_SIZE:
        raise SystemExit(f"only {len(chosen)} rows available -- raise --max-resp-tokens")

    p = chosen.cluster_id.value_counts(normalize=True)
    comp = {
        "mean_total_tokens": float(chosen.total_tokens.mean()),
        "sum_total_tokens": int(chosen.total_tokens.sum()),
        "resp_tokens_median": float(chosen.resp_tokens.median()),
        "unique_prompts": int(chosen.prompt_hash.nunique()),
        "fill_rows": int(len(chosen) - taken.get(0, 0)),
        "tier_counts": {TIER_LABELS[t]: n for t, n in taken.items()},
        "source": chosen.source.value_counts().to_dict(),
        "pass_rate_hist": chosen.pass_rate.round(3).value_counts().sort_index().to_dict(),
        "cluster_entropy_bits": float(-(p * np.log2(p)).sum()),
        "n_clusters": int(p.size),
        "max_cluster_frac": float(p.max()),
    }
    print(f"  composition: {json.dumps({k: v for k, v in comp.items() if k != 'source'}, default=str)[:700]}")
    print(f"  training tokens vs full_method_s1 (~112M): {comp['sum_total_tokens'] / REF_TOKENS:.2f}x")
    if args.dry_run:
        return
    write_subset(name, sorted(chosen.pool_idx.astype(int).tolist()),
                 {"method": METHOD, "seed": args.seed,
                  "config": {"band": list(BAND), "max_resp_tokens": args.max_resp_tokens, "stratify": True,
                             "fill_order": ["pass_rate 0 (R1-majority rule)", "pass_rate 1.0"],
                             "per_prompt": "best tier, majority-agreeing, shortest"},
                  "keep_proof": False, "funnel": funnel, "composition": comp})


if __name__ == "__main__":
    main()
