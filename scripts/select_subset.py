"""Step 5 -- deterministic selection over analysis/pool_scores.parquet.

    python scripts/select_subset.py full_method --seed 1
    python scripts/select_subset.py filter_difficulty --seed 1 --dry-run   # funnel only

Presets (each adds one ingredient to the previous, so the ablations isolate it):
    filter_only        math only; drop truncated / no boxed / ungradeable / proof-like / contaminated
                       (test AND dev) / flagged; one R1 response per prompt; uniform sample
    filter_difficulty  + keep pass_rate in [band_lo, band_hi] (default 0..0.5);
                       drop 0/8 rows whose R1 answer is not a strict majority among R1 responses
    full_method        + stratify across cluster_id (max-min fair quotas, i.e. water-filling)
    hardest_only       filter + pass_rate == 0 (+ the same R1-majority rule), no stratification

Output name: <preset>_s<seed> -> LLaMA-Factory/data/<name>.json, registered as the README does;
the funnel and composition go to data_subsets/<name>.meta.json.
If fewer than 15,000 prompts survive, the remainder is filled with additional R1 responses to
already-selected prompts (majority-agreeing ones first); this is logged in the meta.
"""
import argparse
import json

import numpy as np
import pandas as pd

from common import ANALYSIS, SUBSET_SIZE, write_subset

PRESETS = {
    "filter_only":       {"difficulty": False, "stratify": False, "band": None},
    "filter_difficulty": {"difficulty": True, "stratify": False, "band": (0.0, 0.5)},
    "full_method":       {"difficulty": True, "stratify": True, "band": (0.0, 0.5)},
    "hardest_only":      {"difficulty": True, "stratify": False, "band": (0.0, 0.0)},
}


def waterfill(counts: pd.Series, total: int) -> pd.Series:
    """Max-min fair quotas: every cluster gets the same share, capped by what it has."""
    quota = pd.Series(0, index=counts.index)
    remaining, open_ = total, counts.index.tolist()
    while remaining > 0 and open_:
        share = max(1, remaining // len(open_))
        for c in list(open_):
            take = min(share, counts[c] - quota[c], remaining)
            quota[c] += take
            remaining -= take
            if quota[c] >= counts[c]:
                open_.remove(c)
            if remaining == 0:
                break
    return quota


def sample(df: pd.DataFrame, n: int, rng: np.random.Generator, stratify: bool) -> pd.DataFrame:
    if n >= len(df):
        return df
    if not stratify:
        return df.iloc[rng.choice(len(df), n, replace=False)]
    quota = waterfill(df.groupby("cluster_id").size(), n)
    parts = [g.iloc[rng.choice(len(g), quota[c], replace=False)] for c, g in df.groupby("cluster_id") if quota[c]]
    return pd.concat(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("preset", choices=PRESETS)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--band", type=float, nargs=2, default=None, help="override pass-rate band lo hi")
    ap.add_argument("--keep-proof", action="store_true", help="keep proof_like / text-answer rows")
    ap.add_argument("--name", default=None, help="override output name")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    cfg = dict(PRESETS[args.preset])
    if args.band:
        cfg["band"] = tuple(args.band)
    name = args.name or f"{args.preset}_s{args.seed}"
    rng = np.random.default_rng(args.seed)

    df = pd.read_parquet(ANALYSIS / "pool_scores.parquet")
    funnel = [("pool", len(df))]

    def keep(mask, label):
        nonlocal df
        df = df[mask]
        funnel.append((label, len(df)))

    keep(df.domain == "math", "math")
    keep(~df.truncated, "not truncated (<=16384 tokens)")
    keep(df.has_boxed & (df.answer_kind != "none"), "balanced \\boxed{} in final answer")
    if not args.keep_proof:
        keep(~df.proof_like, "not proof-like / prose answer")
    keep(~df.contam, "not contaminated (test)")
    keep(~df.contam_dev, "not contaminated (dev)")
    keep(~df.flagged, "no repetition / lang-mix / malformed flag")

    if cfg["difficulty"]:
        if "pass_rate" not in df:
            raise SystemExit("pool_scores.parquet has no pass_rate -- run Step 4 first")
        lo, hi = cfg["band"]
        keep(df.pass_rate.notna(), "scored")
        keep(df.pass_rate.between(lo - 1e-9, hi + 1e-9), f"pass_rate in [{lo}, {hi}]")
        noisy = (df.pass_rate == 0) & df.r1_agreement.notna() & ~df.r1_in_majority.fillna(False).astype(bool)
        keep(~noisy, "drop 0/8 rows whose R1 answer is not the R1 majority")
    if cfg["stratify"] and "cluster_id" not in df:
        raise SystemExit("pool_scores.parquet has no cluster_id -- run scripts/embed_cluster.py")
    if "cluster_id" not in df:
        df = df.assign(cluster_id=-1)

    # One response per prompt (prefer majority-agreeing R1 responses), rest kept as fill-in reserve.
    df = df.assign(_pref=df.r1_in_majority.fillna(True).astype(bool) if "r1_in_majority" in df else True,
                   _rand=rng.random(len(df)))
    df = df.sort_values(["prompt_hash", "_pref", "_rand"], ascending=[True, False, True])
    primary = df.drop_duplicates("prompt_hash")
    reserve = df[~df.pool_idx.isin(primary.pool_idx)].sort_values(["_pref", "_rand"], ascending=[False, True])
    funnel.append(("unique prompts (1 response each)", len(primary)))

    chosen = sample(primary, SUBSET_SIZE, rng, cfg["stratify"])
    n_fill = SUBSET_SIZE - len(chosen)
    if n_fill > 0:
        fill = sample(reserve[reserve._pref], n_fill, rng, cfg["stratify"])
        if len(fill) < n_fill:
            fill = pd.concat([fill, reserve[~reserve._pref].head(n_fill - len(fill))])
        chosen = pd.concat([chosen, fill.head(n_fill)])
        n_fill = len(chosen) - len(primary)
    funnel.append(("selected", len(chosen)))

    print(f"\n{name}  ({json.dumps(cfg)})")
    for label, n in funnel:
        print(f"  {n:>7}  {label}")
    if n_fill > 0:
        print(f"  NOTE: only {len(primary)} unique prompts survived; filled {n_fill} with extra R1 responses")
    if len(chosen) < SUBSET_SIZE:
        raise SystemExit(f"only {len(chosen)} rows available -- loosen the filters (e.g. --band 0 0.625)")

    comp = {
        "mean_total_tokens": float(chosen.total_tokens.mean()),
        "sum_total_tokens": int(chosen.total_tokens.sum()),
        "unique_prompts": int(chosen.prompt_hash.nunique()),
        "fill_rows": int(max(n_fill, 0)),
        "source": chosen.source.value_counts().to_dict(),
    }
    if "pass_rate" in chosen:
        comp["pass_rate_hist"] = chosen.pass_rate.round(3).value_counts().sort_index().to_dict()
    if (chosen.cluster_id >= 0).any():
        p = chosen.cluster_id.value_counts(normalize=True)
        comp["cluster_entropy_bits"] = float(-(p * np.log2(p)).sum())
        comp["n_clusters"] = int(p.size)
        comp["max_cluster_frac"] = float(p.max())
    print(f"  composition: {json.dumps({k: v for k, v in comp.items() if k != 'source'}, default=str)[:400]}")
    if args.dry_run:
        return
    write_subset(name, sorted(chosen.pool_idx.astype(int).tolist()),
                 {"method": args.preset, "seed": args.seed, "config": cfg, "keep_proof": args.keep_proof,
                  "funnel": funnel, "composition": comp})


if __name__ == "__main__":
    main()
