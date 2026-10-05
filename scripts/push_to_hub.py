"""Step 7 deliverables: push a trained model and/or a 15K subset to the HF Hub.

    python scripts/push_to_hub.py model   random_s1      <hf_user>/qwen25-3b-acereason-random15k
    python scripts/push_to_hub.py dataset random_s1      <hf_user>/acereason-random15k
Repos are created private; flip them to public on the Hub when submitting.
"""
import argparse
import json

from huggingface_hub import HfApi

from common import LF_DATA, LF_DIR, SAVES, SUBSETS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["model", "dataset"])
    ap.add_argument("run")
    ap.add_argument("repo_id")
    ap.add_argument("--public", action="store_true")
    args = ap.parse_args()
    api = HfApi()
    api.create_repo(args.repo_id, repo_type=args.kind, private=not args.public, exist_ok=True)
    if args.kind == "model":
        folder = SAVES / args.run
        assert (folder / "DONE").exists(), f"{folder} has no DONE marker"
        api.upload_folder(repo_id=args.repo_id, folder_path=str(folder),
                          ignore_patterns=["checkpoint-*", "*.log", "DONE", "hardware.txt", "runs/*"])
        cfg = (LF_DIR / "yamls" / f"{args.run}.yaml").read_text()
        api.upload_file(path_or_fileobj=cfg.encode(), path_in_repo="training_config.yaml", repo_id=args.repo_id)
    else:
        api.upload_file(path_or_fileobj=str(LF_DATA / f"{args.run}.json"), path_in_repo=f"{args.run}.json",
                        repo_id=args.repo_id, repo_type="dataset")
        meta = SUBSETS / f"{args.run}.meta.json"
        api.upload_file(path_or_fileobj=str(meta), path_in_repo="selection_meta.json",
                        repo_id=args.repo_id, repo_type="dataset")
        print(json.loads(meta.read_text()).get("method"))
    print(f"pushed {args.kind} {args.run} -> https://huggingface.co/{'datasets/' if args.kind == 'dataset' else ''}{args.repo_id}")


if __name__ == "__main__":
    main()
