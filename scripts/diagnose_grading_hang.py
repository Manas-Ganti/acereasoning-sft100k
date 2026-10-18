"""Find which sample makes eval.py's grading hang, from the completions pickle eval.py saved (CPU only, no GPU).

    # login node or any CPU job, from the repo root:
    ~/.conda/envs/evalenv/bin/python scripts/diagnose_grading_hang.py random_s1 minerva

Why: random_s1 minerva (7999727) finished generating in ~1 h, then sat in "check correct..." until the 10 h
TIMEOUT. eval/utils/grader.py:call_with_timeout does `process.join(3)` and then `output_queue.get()` with no
timeout: if the sympy child dies hard (segfault / C stack overflow in sympy or antlr) without putting a
result, the parent blocks forever. eval.py pickles the vLLM outputs BEFORE grading, so nothing is lost.

This replays eval.py's grading loop with eval's own, unmodified functions (parse_ground_truth, extract_answer,
check_is_correct), each sample in a forked child with a wall-clock watchdog, and reports the samples that hang.
If none hang it also prints Acc / Pass@1 computed exactly as eval.py does. It writes nothing under eval/.
Diagnostic only: those numbers are NOT an official score until a human decides how to treat the hang.
"""
import argparse
import multiprocessing as mp
import pickle
import sys
import time

from common import EVAL_DIR, REPO

sys.path.insert(0, str(EVAL_DIR))
from utils.data_loader import load_data  # noqa: E402
from utils.grader import check_is_correct  # noqa: E402
from utils.parser import extract_answer, parse_ground_truth  # noqa: E402


def grade_one(example, responses, bench, q):
    # mirrors eval.py's "check correct..." loop body
    _, gt_ans = parse_ground_truth(example, bench)
    answers = [extract_answer(r, bench) for r in responses]
    q.put([check_is_correct(a, gt_ans) for a in answers])  # small payload: a big put blocks the child's exit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("bench")
    ap.add_argument("--watchdog", type=int, default=120, help="seconds per sample before it counts as hung")
    args = ap.parse_args()

    pkls = sorted((REPO / "eval" / "outputs" / args.run / "completions").glob(f"**/{args.bench}/*_gen_round*.pkl"))
    if not pkls:
        sys.exit(f"no completions pickle for {args.run}/{args.bench}")
    examples = load_data(args.bench, "test", str(EVAL_DIR / "data"))
    rounds = []
    for p in pkls:
        print(f"loading {p.relative_to(REPO)}")
        with open(p, "rb") as f:
            rounds.append(pickle.load(f))
    assert all(len(c) == len(examples) for c in rounds), "pickle / dataset length mismatch"

    ctx = mp.get_context("fork")
    hung, correct, pass1 = [], 0, []
    t0 = time.time()
    for i, ex in enumerate(examples):
        responses = [o.text for c in rounds for o in c[i].outputs]
        q = ctx.Queue()
        p = ctx.Process(target=grade_one, args=(ex, responses, args.bench, q))
        p.start()
        p.join(args.watchdog)
        if p.is_alive() or q.empty():
            state = "HUNG" if p.is_alive() else f"DIED (exitcode {p.exitcode})"
            if p.is_alive():
                p.kill()
                p.join()
            answers = [extract_answer(r, args.bench) for r in responses]
            _, gt = parse_ground_truth(ex, args.bench)
            hung.append(i)
            print(f"[{i}] {state}: gold={gt!r}")
            for j, a in enumerate(answers):
                print(f"      sample {j}: answer={a[:300]!r} (len {len(a)})")
            continue
        ok = q.get()
        correct += any(ok)
        pass1.append(sum(ok) / len(ok))
        if (i + 1) % 25 == 0:
            print(f"{i + 1}/{len(examples)} graded, {time.time() - t0:.0f} s")

    print(f"\n{len(hung)} of {len(examples)} samples hung or died: {hung}")
    if not hung:
        print(f"Acc: {correct / len(examples):.4f}   Pass@1: {sum(pass1) / len(pass1):.4f}   (diagnostic, not official)")


if __name__ == "__main__":
    main()
