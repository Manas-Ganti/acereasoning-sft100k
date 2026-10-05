"""Step 3 -- uniform random 15K subsets of the full 100K pool (no filtering: this IS the baseline).

    python scripts/make_random_subsets.py --seeds 1 2
-> LLaMA-Factory/data/random_s{1,2}.json + dataset_info.json entry (README section 3);
   provenance in data_subsets/random_s{1,2}.meta.json / .idx.txt
"""
import argparse

import numpy as np

from common import ANALYSIS, SUBSET_SIZE, load_pool, write_subset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    args = ap.parse_args()
    n = len(load_pool(["pool_idx"]))
    for seed in args.seeds:
        idx = np.random.default_rng(seed).choice(n, size=SUBSET_SIZE, replace=False)
        meta = {"method": "uniform random over the 100K pool", "seed": seed}
        audit_path = ANALYSIS / "pool_audit.parquet"
        if audit_path.exists():  # describe what the random subset contains (for the report)
            import pandas as pd
            a = pd.read_parquet(audit_path).set_index("pool_idx").loc[idx]
            meta["composition"] = {"math_frac": float((a.domain == "math").mean()),
                                   "truncated_frac": float(a.truncated.mean()),
                                   "contam_rows": int(a.contam.sum()),
                                   "mean_total_tokens": float(a.total_tokens.mean())}
        write_subset(f"random_s{seed}", sorted(idx.tolist()), meta)


if __name__ == "__main__":
    main()
