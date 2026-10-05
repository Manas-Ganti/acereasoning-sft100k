"""Step 4c -- sentence embeddings of the math prompts + k-means topics. 1 GPU, ~15 min.

    submitted by launch/score_pool.sh       (k=100 by default; K=150 launch/score_pool.sh to change)

Writes analysis/pool_clusters.parquet (pool_idx, cluster_id; -1 for non-math rows),
work/scores/prompt_emb.npy, and analysis/clusters_spotcheck.md: size, top terms and example
prompts for every cluster. READ IT -- spot-check that clusters are topics, not formatting artefacts.
"""
import argparse

import numpy as np
import pandas as pd

from common import ANALYSIS, WORK, load_pool, md_table, user_prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=100)
    ap.add_argument("--model", default="BAAI/bge-base-en-v1.5")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    audit = pd.read_parquet(ANALYSIS / "pool_audit.parquet", columns=["pool_idx", "domain", "prompt_hash"])
    math = audit[audit.domain == "math"].sort_values("pool_idx")
    uniq = math.drop_duplicates("prompt_hash")
    pool = load_pool(["pool_idx", "instruction", "input"]).set_index("pool_idx")
    texts = [user_prompt(pool.at[p, "instruction"], pool.at[p, "input"]) for p in uniq.pool_idx]
    print(f"embedding {len(texts)} unique math prompts with {args.model}")

    emb_path = WORK / "scores" / "prompt_emb.npy"
    if emb_path.exists() and np.load(emb_path, mmap_mode="r").shape[0] == len(texts):
        emb = np.load(emb_path)
    else:
        from sentence_transformers import SentenceTransformer
        m = SentenceTransformer(args.model, device="cuda")
        m.max_seq_length = 384
        emb = m.encode(texts, batch_size=256, normalize_embeddings=True, show_progress_bar=True)
        emb_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(emb_path, emb.astype(np.float32))

    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=args.k, n_init=4, random_state=args.seed).fit(emb)
    lab = pd.Series(km.labels_, index=uniq.prompt_hash.values)

    out = audit[["pool_idx", "prompt_hash"]].copy()
    out["cluster_id"] = out.prompt_hash.map(lab).fillna(-1).astype(int)
    out[["pool_idx", "cluster_id"]].to_parquet(ANALYSIS / "pool_clusters.parquet")

    # Spot-check report: top TF-IDF terms + nearest-to-centroid examples per cluster.
    from sklearn.feature_extraction.text import TfidfVectorizer
    tf = TfidfVectorizer(max_features=30000, stop_words="english", token_pattern=r"[A-Za-z]{3,}")
    X = tf.fit_transform(texts)
    vocab = np.array(tf.get_feature_names_out())
    dist = km.transform(emb)
    L = [f"# Cluster spot-check (k={args.k}, {args.model}, {len(texts)} unique math prompts)", "",
         "Each cluster: size, top terms, the 3 prompts nearest its centroid. Look for clusters that are "
         "formatting artefacts (e.g. 'answer in the form') instead of topics.", ""]
    sizes = np.bincount(km.labels_, minlength=args.k)
    L += [md_table(pd.DataFrame({"min": [sizes.min()], "median": [int(np.median(sizes))], "max": [sizes.max()]})), ""]
    for c in np.argsort(-sizes):
        members = np.where(km.labels_ == c)[0]
        terms = vocab[np.asarray(X[members].mean(axis=0)).ravel().argsort()[::-1][:8]]
        L.append(f"## cluster {c} -- {sizes[c]} prompts -- {', '.join(terms)}")
        for i in members[np.argsort(dist[members, c])[:3]]:
            L.append(f"- {texts[i][:220].replace(chr(10), ' ')}")
        L.append("")
    (ANALYSIS / "clusters_spotcheck.md").write_text("\n".join(L))
    print(f"wrote pool_clusters.parquet and clusters_spotcheck.md (sizes min {sizes.min()} max {sizes.max()})")

    from build_pool_scores import build
    build()


if __name__ == "__main__":
    main()
