"""Generate LLaMA-Factory/yamls/<run>.yaml from yamls/_template.yaml (the README YAML) and verify
it differs from the template only in `dataset` and `output_dir`.

    python scripts/make_config.py random_s1 [random_s2 ...]   # run name == subset name
    python scripts/make_config.py --check random_s1           # verify only (train.slurm does this)
"""
import argparse
import json
import sys

from common import LF_DATA, LF_DIR

YAMLS = LF_DIR / "yamls"
TEMPLATE = YAMLS / "_template.yaml"
VARYING = {"dataset", "output_dir"}


def parse(text):
    out = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].rstrip()
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def check(run):
    path = YAMLS / f"{run}.yaml"
    if not path.exists():
        sys.exit(f"{path} missing: python scripts/make_config.py {run}")
    base, cfg = parse(TEMPLATE.read_text()), parse(path.read_text())
    diff = {k for k in base.keys() | cfg.keys() if base.get(k) != cfg.get(k)} - VARYING
    if diff:
        sys.exit(f"{path.name}: differs from _template.yaml in {sorted(diff)} -- comparison runs must differ only in data")
    if cfg["output_dir"] != f"saves/qwen25_3b_instruct/{run}":
        sys.exit(f"{path.name}: output_dir must be saves/qwen25_3b_instruct/{run}")
    info = json.loads((LF_DATA / "dataset_info.json").read_text(encoding="utf-8"))
    ds = cfg["dataset"]
    if ds not in info or not (LF_DATA / info[ds]["file_name"]).exists():
        sys.exit(f"{path.name}: dataset '{ds}' not registered in LLaMA-Factory/data/dataset_info.json or file missing")
    print(f"ok  yamls/{path.name}  (dataset={ds})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    for run in args.runs:
        if not args.check:
            text = TEMPLATE.read_text().replace("__DATASET__", run).replace("__RUN__", run)
            (YAMLS / f"{run}.yaml").write_text(text)
        check(run)


if __name__ == "__main__":
    main()
