"""Second smart selection (added 2026-10-13): the 15,000 longest clean math traces.

    python scripts/select_longest.py --seed 1 --dry-run     # funnel + composition, writes nothing
    python scripts/select_longest.py --seed 1               # -> longest_s1

Hypothesis (LIMO, s1): for small-model reasoning SFT, long and hard R1 traces carry the most signal.
Where full_method picks by base-model difficulty and topic balance, this picks by trace length.

Procedure, deterministic:
  1. The same quality filter as every select_subset.py preset: math only; drop truncated, no balanced
     \\boxed{}, proof-like / prose answer, contaminated (test AND dev), flagged.
  2. The same label-noise rule as the difficulty presets: drop pass_rate-0 rows whose R1 answer is not
     the R1 majority (a long trace with a wrong answer is the case it guards against).
  3. One response per prompt: prefer majority-agreeing R1 responses, then the longest.
  4. Take the 15,000 longest by resp_tokens (Qwen2.5 tokens); ties broken by pool_idx.
The seed only names the run (`_s<seed>`): no step is random. Reuses common.write_subset, so the output
(LLaMA-Factory/data/<name>.json, dataset_info.json entry, data_subsets/<name>.meta.json + .idx.txt) is
exactly what select_subset.py writes, and subset_from_idx.py / make_config.py / launch/train.sh work unchanged.

Expect more training tokens than random (~112M): the meta records sum_total_tokens, and the report must
state the ratio, since compute then differs from the random baselines.
"""
import argparse
import json

import numpy as np
import pandas as pd

from common import ANALYSIS, SUBSET_SIZE, write_subset

METHOD = "longest"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1, help="names the run only; selection is not random")
    ap.add_argument("--name", default=None, help="override output name (default longest_s<seed>)")
    ap.add_argument("--scores", default=str(ANALYSIS / "pool_scores.parquet"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    name = args.name or f"{METHOD}_s{args.seed}"

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
    if "pass_rate" not in df:
        raise SystemExit("pool_scores.parquet has no pass_rate -- run Step 4 first")
    noisy = (df.pass_rate == 0) & df.r1_agreement.notna() & ~df.r1_in_majority.fillna(False).astype(bool)
    keep(~noisy, "drop pass_rate-0 rows whose R1 answer is not the R1 majority")

    # One response per prompt: majority-agreeing first, then the longest, then lowest pool_idx.
    df = df.assign(_pref=df.r1_in_majority.fillna(True).astype(bool))
    df = df.sort_values(["prompt_hash", "_pref", "resp_tokens", "pool_idx"], ascending=[True, False, False, True])
    primary = df.drop_duplicates("prompt_hash")
    funnel.append(("unique prompts (1 response each)", len(primary)))
    if len(primary) < SUBSET_SIZE:
        raise SystemExit(f"only {len(primary)} unique prompts survive -- fewer than {SUBSET_SIZE}")

    ranked = primary.sort_values(["resp_tokens", "pool_idx"], ascending=[False, True])
    chosen = ranked.head(SUBSET_SIZE)
    funnel.append((f"{SUBSET_SIZE} longest by resp_tokens", len(chosen)))

    comp = {
        "mean_total_tokens": float(chosen.total_tokens.mean()),
        "sum_total_tokens": int(chosen.total_tokens.sum()),
        "resp_tokens_min": int(chosen.resp_tokens.min()),
        "resp_tokens_median": float(chosen.resp_tokens.median()),
        "resp_tokens_median_unselected": float(ranked.iloc[SUBSET_SIZE:].resp_tokens.median()),
        "unique_prompts": int(chosen.prompt_hash.nunique()),
        "fill_rows": 0,
        "source": chosen.source.value_counts().to_dict(),
        "pass_rate_hist": chosen.pass_rate.round(3).value_counts(dropna=False).sort_index().to_dict(),
    }
    if "cluster_id" in chosen and (chosen.cluster_id >= 0).any():
        p = chosen.cluster_id.value_counts(normalize=True)
        comp["cluster_entropy_bits"] = float(-(p * np.log2(p)).sum())
        comp["n_clusters"] = int(p.size)
        comp["max_cluster_frac"] = float(p.max())

    print(f"\n{name}  (method={METHOD})")
    for label, n in funnel:
        print(f"  {n:>7}  {label}")
    print(f"  composition: {json.dumps({k: v for k, v in comp.items() if k != 'source'}, default=str)[:600]}")
    print(f"  training tokens vs random (~112M): {comp['sum_total_tokens'] / 112e6:.2f}x")
    if args.dry_run:
        return
    write_subset(name, sorted(chosen.pool_idx.astype(int).tolist()),
                 {"method": METHOD, "seed": args.seed, "config": {"rank_by": "resp_tokens", "order": "desc"},
                  "keep_proof": False, "funnel": funnel, "composition": comp})


if __name__ == "__main__":
    main()
