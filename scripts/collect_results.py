"""Collect eval results into results/results.csv + results/results.md.

    python scripts/collect_results.py                 # test benchmarks, all runs in eval/outputs/
    python scripts/collect_results.py --gate base     # Step 2 gate: is the eval environment sane?
    python scripts/collect_results.py --dev           # dev-set results (work/dev_eval/)

Scores are recomputed from the per-sample jsonl (answers_correctness), which is what the log's
Pass@1 line reports. Also reported: boxed_rate = share of samples with a non-empty \\boxed{} answer
(post-SFT models that learned truncated traces stop without one).

Noise accounting (printed whenever >= 2 random_* runs exist):
  * seed spread  = max - min over random runs (training/data-sampling noise -- the bar to clear)
  * bootstrap CI = 95% CI of (run - random mean) from resampling problems within each benchmark
                   (eval-sampling noise only; does NOT include seed noise)
"""
import argparse
import json
import math
import sys

import numpy as np
import pandas as pd

from common import BASELINE_REF, BENCHMARKS, EVAL_DIR, LB_VISIBLE, RESULTS, WORK, md_table


def load_run(run_dir, benches):
    out = {}
    for b in benches:
        files = sorted(run_dir.glob(f"**/{b}/test_*.jsonl"))
        if not files:
            continue
        rows = [json.loads(l) for l in open(files[-1], encoding="utf-8")]
        per_q = np.array([np.mean(r["answers_correctness"]) for r in rows])
        boxed = np.mean([np.mean([bool(a) for a in r["generated_answers"]]) for r in rows])
        out[b] = {"n": len(rows), "pass1": float(per_q.mean()),
                  "pass8": float(np.mean([any(r["answers_correctness"]) for r in rows])),
                  "boxed_rate": float(boxed), "per_q": per_q}
    return out


def avg(scores, benches):
    vals = [scores[b]["pass1"] for b in benches if b in scores]
    return float(np.mean(vals)) if len(vals) == len(benches) else float("nan")


def bootstrap_gap(a, b, benches, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    diffs = np.zeros(n_boot)
    for b_ in benches:
        pa, pb = a[b_]["per_q"], b[b_]["per_q"]
        if len(pa) != len(pb):
            return float("nan"), float("nan")
        idx = rng.integers(0, len(pa), size=(n_boot, len(pa)))
        diffs += (pa[idx].mean(1) - pb[idx].mean(1)) / len(benches)
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))


def gate(scores):
    print("\n## Step 2 gate: base model vs Fall-2025 BASELINE row (Pass@1)\n")
    ok, rows = True, []
    for b in BENCHMARKS:
        if b not in scores:
            rows.append([b, "-", BASELINE_REF[b], "-", "-", "MISSING"])
            ok = False
            continue
        p, n, ref = scores[b]["pass1"], scores[b]["n"], BASELINE_REF[b]
        tol = max(0.03, 3 * math.sqrt(max(ref * (1 - ref), 0.01) / n))
        good = abs(p - ref) <= tol
        ok &= good
        rows.append([b, f"{p:.3f}", f"{ref:.3f}", f"{p - ref:+.3f}", f"+-{tol:.3f}", "ok" if good else "OFF"])
    lb, lb_ref = avg(scores, LB_VISIBLE), float(np.mean([BASELINE_REF[b] for b in LB_VISIBLE]))
    ok &= abs(lb - lb_ref) <= 0.03  # per-benchmark tolerances on 30-problem sets are loose; the mean is not
    print(md_table(pd.DataFrame(rows, columns=["benchmark", "ours", "ref", "diff", "tolerance", "status"])))
    print(f"\nLB-visible avg (6 benches, no AIME25): ours {lb:.3f} vs ref {lb_ref:.3f} (must be within 0.03)")
    print("\nGATE: " + ("PASS -- eval environment reproduces the baseline." if ok else
                        "FAIL -- STOP. Fix the eval environment before any training comparison."))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--gate", metavar="RUN", default=None)
    args = ap.parse_args()

    root = WORK / "dev_eval" if args.dev else EVAL_DIR / "outputs"
    if args.dev:
        from common import DEV_DIR
        benches = sorted(p.name for p in (DEV_DIR / "data").iterdir())
        lb = benches
    else:
        benches, lb = BENCHMARKS, LB_VISIBLE
    runs = {d.name: load_run(d, benches) for d in sorted(root.iterdir()) if d.is_dir()} if root.exists() else {}
    runs = {k: v for k, v in runs.items() if v}
    if not runs:
        sys.exit(f"no results under {root}")

    if args.gate:
        sys.exit(0 if gate(runs[args.gate]) else 1)

    recs = [{"run": r, "benchmark": b, **{k: v for k, v in s.items() if k != "per_q"}}
            for r, sc in runs.items() for b, s in sc.items()]
    df = pd.DataFrame(recs)
    tag = "dev_" if args.dev else ""
    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / f"{tag}results.csv", index=False)

    order = sorted(runs, key=lambda r: (r != "base", not r.startswith("random"), r))
    table = []
    for r in order:
        sc = runs[r]
        table.append([r] + [f"{sc[b]['pass1']:.3f}" if b in sc else "-" for b in benches]
                     + [f"{avg(sc, benches):.3f}", f"{avg(sc, lb):.3f}"])
    cols = ["run"] + benches + ["avg(all)"] + ([] if args.dev else ["avg(LB6)"])
    if args.dev:
        table = [t[:-1] for t in table]
    L = [f"# {'Dev' if args.dev else 'Test'} results (Pass@1, temp 0.6, n={'4' if args.dev else '8'})", "",
         md_table(pd.DataFrame(table, columns=cols)), ""]
    if not args.dev:
        L += ["avg(LB6) = CN_MATH_24, KAOYAN, AMC, MINERVA, OLYMPIADBENCH, GPQA (leaderboard AVG minus "
              "AIME25, which is not in eval/data).", ""]
        bx = [[r] + [f"{runs[r][b]['boxed_rate']:.2f}" if b in runs[r] else "-" for b in benches] for r in order]
        L += ["## boxed_rate (share of samples with a \\boxed{} answer)", "",
              md_table(pd.DataFrame(bx, columns=["run"] + benches)), ""]

    metric_benches = lb
    rand = [r for r in order if r.startswith("random") and all(b in runs[r] for b in metric_benches)]
    if len(rand) >= 2:
        ravg = [avg(runs[r], metric_benches) for r in rand]
        spread = max(ravg) - min(ravg)
        mean_r = float(np.mean(ravg))
        L += ["## Comparison vs random (noise-aware)", "",
              f"Random runs: {', '.join(f'{r}={v:.3f}' for r, v in zip(rand, ravg))}; "
              f"mean {mean_r:.3f}; **seed spread {spread:.3f}**.", ""]
        rows = []
        for r in order:
            if r in rand or r == "base" or not all(b in runs[r] for b in metric_benches):
                continue
            gap = avg(runs[r], metric_benches) - mean_r
            cis = [bootstrap_gap(runs[r], runs[x], metric_benches) for x in rand]
            ci = f"[{min(c[0] for c in cis):+.3f}, {max(c[1] for c in cis):+.3f}]"
            verdict = "exceeds seed spread" if gap > spread else ("within noise" if gap > -spread else "worse")
            rows.append([r, f"{avg(runs[r], metric_benches):.3f}", f"{gap:+.3f}", ci, verdict])
        if rows:
            L += [md_table(pd.DataFrame(rows, columns=["run", "avg", "gap vs random mean",
                                                       "bootstrap 95% CI (vs each random)", "verdict"])), "",
                  "A gap smaller than the seed spread is not an improvement.", ""]
    (RESULTS / f"{tag}results.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
