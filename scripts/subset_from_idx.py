"""Rebuild a committed subset from its row list, on an account that lacks analysis/pool_scores.parquet.

    python scripts/subset_from_idx.py full_method_s1 [more names ...]

Reads data_subsets/<name>.idx.txt (committed by whoever ran select_subset.py), checks it against the
pool_idx_sha256 in data_subsets/<name>.meta.json, and writes LLaMA-Factory/data/<name>.json + the
dataset_info.json entry via write_subset (same records, same registration). Needs only the pool
(scripts/fetch_data.py). Refuses to write if the hash differs.
"""
import argparse
import hashlib
import json

from common import SUBSETS, write_subset

# keys write_subset recomputes itself
DERIVED = {"name", "n", "pool_idx_sha256", "rows_with_system_not_eval_prompt"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    args = ap.parse_args()
    for name in args.names:
        meta = json.loads((SUBSETS / f"{name}.meta.json").read_text())
        idx = [int(x) for x in (SUBSETS / f"{name}.idx.txt").read_text().split()]
        digest = hashlib.sha256(",".join(map(str, sorted(idx))).encode()).hexdigest()
        if digest != meta["pool_idx_sha256"]:
            raise SystemExit(f"{name}: idx.txt hash {digest[:12]} != meta {meta['pool_idx_sha256'][:12]}")
        write_subset(name, idx, {k: v for k, v in meta.items() if k not in DERIVED})
        print(f"{name}: rebuilt {len(idx)} rows, sha256 {digest[:12]} matches")


if __name__ == "__main__":
    main()
