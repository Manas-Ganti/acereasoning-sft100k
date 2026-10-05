"""README section 1.5: download the 100K subset file, plus the base model into HF_HOME.

    python scripts/fetch_data.py        (login node; network-bound)

Downloads exactly what the README names:
    hf_hub_download(repo_id="redsgnaoh/acereason11_100k", repo_type="dataset",
                    filename="data/acereason11_100k.json", local_dir=work/pool)
and caches it as work/pool/pool.parquet (pool_idx = row position in the JSON) with columns
    pool_idx, instruction, input, output, system, category, source, src_index
"""
import json

import pandas as pd
from huggingface_hub import hf_hub_download, snapshot_download

from common import BASE_MODEL, POOL_FILE, POOL_PARQUET, POOL_REPO, WORK


def main():
    p = hf_hub_download(repo_id=POOL_REPO, repo_type="dataset", filename=POOL_FILE, local_dir=WORK / "pool")
    print(f"pool file: {p}")
    with open(p, encoding="utf-8") as f:
        rows = json.load(f)
    df = pd.DataFrame(rows)
    info = pd.json_normalize(df.pop("extra_info"))
    df["category"] = info["category"].values
    df["source"] = info["source"].values
    df["src_index"] = info["index"].values
    df["input"] = df["input"].fillna("")
    df.insert(0, "pool_idx", range(len(df)))
    assert len(df) == 100_000, len(df)
    df.to_parquet(POOL_PARQUET, compression="zstd")
    print(f"pool: {len(df)} rows -> {POOL_PARQUET}")
    print(df["category"].value_counts().to_string())

    snapshot_download(BASE_MODEL, allow_patterns=["*.json", "*.safetensors", "*.txt", "*.model"])
    print(f"base model cached: {BASE_MODEL}")


if __name__ == "__main__":
    main()
