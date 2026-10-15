"""Make a trained model's tokenizer loadable by evalenv (transformers 4.44.2 / older `tokenizers`).

Training runs in myenv (transformers 4.55), whose `tokenizers` writes tokenizer.json with BPE merges as
[a, b] pairs. evalenv's older `tokenizers` cannot parse that:
    Exception: data did not match any variant of untagged enum ModelWrapper at line ... column 3
(first seen 2026-10-15: every random_s1 eval crashed in under a minute).

SFT does not change the tokenizer, so the base model's tokenizer.json (old "a b" merge strings) holds the
same vocab and merges. This script checks that field by field -- vocab, merges, added tokens, normalizer,
pre-tokenizer, decoder, post-processor -- and only then swaps the file in, keeping the trained one as
tokenizer.json.trained. If tokenizer_config.json has no chat_template (newer transformers saves it to
chat_template.jinja, which 4.44.2 ignores, so eval.py's apply_chat_template would fail), the trained model's own
chat_template.jinja is copied into it (backup tokenizer_config.json.trained). The check applies the template as eval does. eval/ is
not touched. Idempotent.

    ~/.conda/envs/evalenv/bin/python scripts/fix_tokenizer_for_eval.py random_s1 random_s2
"""
import argparse
import json
import shutil
import sys

from common import BASE_MODEL, SAVES


def merges_as_strings(tok):
    return [m if isinstance(m, str) else " ".join(m) for m in tok["model"].get("merges", [])]


def compare(trained, base):
    diffs = []
    for key in ("normalizer", "pre_tokenizer", "post_processor", "decoder"):
        if trained.get(key) != base.get(key):
            diffs.append(key)
    if trained["model"].get("vocab") != base["model"].get("vocab"):
        diffs.append("model.vocab")
    if merges_as_strings(trained) != merges_as_strings(base):
        diffs.append("model.merges")
    added = lambda t: [(a["id"], a["content"], a.get("special")) for a in t.get("added_tokens", [])]
    if added(trained) != added(base):
        diffs.append("added_tokens")
    return diffs


def loads_here(model_dir):
    """Load the tokenizer AND apply its chat template, as eval.py does (--surround_with_messages)."""
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(str(model_dir), trust_remote_code=True)
        tok.apply_chat_template([{"role": "user", "content": "1+1?"}], tokenize=False, add_generation_prompt=True)
        return True, ""
    except Exception as e:  # noqa: BLE001 -- the tokenizers error is a bare Exception
        return False, str(e).splitlines()[0]


def fix_chat_template(model_dir, run):
    """transformers >= 4.5x saves the chat template to chat_template.jinja; 4.44.2 reads it only from
    tokenizer_config.json["chat_template"]. Copy the trained model's own template in (no content change)."""
    jinja, cfg_path = model_dir / "chat_template.jinja", model_dir / "tokenizer_config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    if cfg.get("chat_template") or not jinja.exists():
        return False
    backup = model_dir / "tokenizer_config.json.trained"
    if not backup.exists():
        shutil.copy2(cfg_path, backup)
    cfg["chat_template"] = jinja.read_text(encoding="utf-8")
    cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[{run}] copied chat_template.jinja into tokenizer_config.json; backup -> {backup.name}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    args = ap.parse_args()
    from huggingface_hub import hf_hub_download
    base_path = hf_hub_download(BASE_MODEL, "tokenizer.json")
    base = json.loads(open(base_path, encoding="utf-8").read())
    bad = 0
    for run in args.runs:
        d = SAVES / run
        tj = d / "tokenizer.json"
        if not tj.exists():
            print(f"[{run}] no {tj}"); bad += 1; continue
        fix_chat_template(d, run)
        ok, err = loads_here(d)
        if ok:
            print(f"[{run}] tokenizer + chat template work in this env -- ok"); continue
        print(f"[{run}] does not load here: {err}")
        trained = json.loads(tj.read_text(encoding="utf-8"))
        diffs = compare(trained, base)
        if diffs:
            print(f"[{run}] REFUSING: trained tokenizer differs from {BASE_MODEL} in {diffs}"); bad += 1; continue
        backup = d / "tokenizer.json.trained"
        if not backup.exists():
            shutil.copy2(tj, backup)
        shutil.copyfile(base_path, tj)
        ok, err = loads_here(d)
        print(f"[{run}] swapped in base tokenizer.json (same vocab/merges/added tokens); "
              f"backup -> {backup.name}; loads now: {ok} {err}")
        bad += not ok
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
