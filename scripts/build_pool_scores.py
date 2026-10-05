"""Join audit + grades + clusters into analysis/pool_scores.parquet (one row per pool sample).

Called automatically at the end of score_pool_grade.py and embed_cluster.py; whichever runs
last produces the complete table. Safe to run by hand:  python scripts/build_pool_scores.py
"""
import pandas as pd

from common import ANALYSIS


def build():
    df = pd.read_parquet(ANALYSIS / "pool_audit.parquet")
    for name in ["pool_grades", "pool_clusters"]:
        p = ANALYSIS / f"{name}.parquet"
        if p.exists():
            df = df.merge(pd.read_parquet(p), on="pool_idx", how="left")
        else:
            print(f"  ({name}.parquet not built yet)")
    out = ANALYSIS / "pool_scores.parquet"
    df.to_parquet(out, compression="zstd")
    have = [c for c in ["pass_rate", "r1_agreement", "cluster_id"] if c in df]
    print(f"wrote {out}: {len(df)} rows, score columns present: {have}")
    return df


if __name__ == "__main__":
    build()
