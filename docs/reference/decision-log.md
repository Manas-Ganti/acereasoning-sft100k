---
title: Decision log
tags: [reference, decisions]
---

# Decision log

← [Home](../00-home.md) · [STATUS](../STATUS.md)

Every deliberate choice that affects results or reproducibility, newest first. **Add an entry whenever you decide
something; don't silently change behaviour.** Format: what was decided, why, and who decided.

> [!NOTE]
> Standing policy: the course README's steps are followed literally and win over CLAUDE.md where they conflict.
> The course repo's tested requirement files are used as written. We deviate only where a step is literally broken,
> and each deviation is listed in [Upstream compliance](upstream-compliance.md).

---

### 2026-10-15: vLLM workers use "spawn" in evalenv (2-GPU evals crashed)
The first 2-GPU trained-model eval died with `RuntimeError: Cannot re-initialize CUDA in forked subprocess`.
`eval.py` calls `set_seed()`, which initialises CUDA, before it creates `vllm.LLM`. With tensor parallel 2, vLLM 0.6.1
forks a worker, and the fork can't use CUDA. 1-GPU evals have no worker, so the base evals never hit this. The
2026-10-10 "2 GPUs for trained models" setting had never actually run: the 2× A100 OlympiadBench copy lost its race
to H200. Fix: `VLLM_WORKER_MULTIPROC_METHOD=spawn`, installed as a conda activate hook in evalenv
(`env/vllm_spawn_hook.sh`). `eval_single.sh` runs `source activate`, so the hook also covers eval jobs **already
queued**. `eval_model.sh` exports it too. `eval.py` keeps its main code under `if __name__ == "__main__"`, so spawn
is safe. This only changes how processes start: sampling and grading are untouched, and `eval/` is unchanged.
*Decided by: Mrunmay.*

---

### 2026-10-15: Trained models get the base model's tokenizer.json for eval
All 8 `random_s1` evals crashed at load: `Exception: data did not match any variant of untagged enum ModelWrapper`.
myenv (transformers 4.55) saves `tokenizer.json` in the newer `tokenizers` format, with merges as [a, b] pairs.
evalenv (transformers 4.44.2, pinned for vllm 0.6.1) can't read it. SFT doesn't change the tokenizer, so
`scripts/fix_tokenizer_for_eval.py` compares the trained file with the base model's field by field: vocab, merges,
added tokens, normalizer, pre-tokenizer, decoder and post-processor. Only if they're identical does it swap in the
base file, keeping the original as `tokenizer.json.trained`. `tokenizer_config.json` (the chat template) stays as
trained, except that if it has no `chat_template` (newer transformers writes it to `chat_template.jinja`, which 4.44.2
ignores, so `eval.py`'s `apply_chat_template` would fail), the trained model's own `chat_template.jinja` is copied in
unchanged. `eval/` is untouched, and the text-to-token mapping is the same. `slurm/train.slurm` now runs the fix
before its job exits. Jobs submitted earlier ran an older copy of the script, so their models need the fix run by
hand. *Decided by: Mrunmay.*

---

### 2026-10-13: A second smart method, `longest_s1`, is trained; the smart model is chosen on the dev set
Manas approved trying another smart selection, which reverses part of the 2026-10-12 "required runs only" entry.
The new method (`scripts/select_longest.py`; no existing script changed) keeps `full_method`'s quality filter and
R1-majority rule, takes one response per prompt, then the 15,000 longest traces. It's motivated by LIMO and s1 (long,
hard traces carry the most signal for small-model reasoning SFT) and differs clearly from `full_method`, which picks
by difficulty and topic balance. **Rule fixed before any result exists:** the smart model we keep, report as "the
smart model" and submit, is the one with the higher **mean dev Pass@1** over the four dev sets. If the gap is under 1
point, keep `full_method_s1` (the pre-planned method). Test-benchmark scores never decide it. Both smart runs are
reported against random. `longest_s1` trains on more tokens than random; the report states the ratio.
*Decided by: Manas (approval relayed by Sahasree).*

### 2026-10-10: evalenv pyarrow walked down to a NumPy-1.26-compatible release
A fresh evalenv build (Mrunmay's account) got `datasets` 5.0.1, pandas 3.0.6 and pyarrow 26.0.0 from the unpinned
`datasets` in `eval/requirements.txt`. pyarrow 26 needs NumPy 2, but vllm 0.6.1 keeps numpy 1.26.4, so `import
pyarrow` fails. That breaks parquet I/O, `build_dev_set.py` and **`eval/` itself, which imports `datasets`**.
`env/fix_evalenv_arrow.sh` keeps numpy/torch/transformers/tokenizers/vllm frozen and lowers pyarrow one major at a
time (pip moves `datasets`, and pandas<3 only if needed) until imports and a parquet round trip pass. `setup_envs.sh`
now runs it. Manas could not be reached to copy his exact versions. Teammates' evalenvs may therefore differ in these
three packages. They don't touch sampling or grading, and subset identity is checked by `pool_idx_sha256`.
*Decided by: Mrunmay.*

---

### 2026-10-10: Training runs are raced across the three teammates' ARC accounts
GPU allocation is the bottleneck, so each of the three teammates submits the same training run from their own ARC
login (all on account `tml_2026`), and the team keeps whichever copy is usable first. Rules, so that the result
stays valid:
1. **Identical inputs.** Everyone generates the subset with the same script and seed. The `pool_idx_sha256` in
   `data_subsets/<run>.meta.json` must match the committed one, and `make_config.py --check` must pass. A copy whose
   hash differs is invalid.
2. **The winner is the first copy whose training finishes** (a `DONE` marker), decided before any eval score exists.
   We never keep the copy with the better scores: that would select on the test benchmarks.
3. **Same hardware class as the other comparison runs:** 8× A100 (the default), global batch 64. `hardware.txt`
   records it.
4. As soon as a winner exists, the others `scancel` their copy of that run *and* its chained eval/dev-eval jobs.
   The winner's owner records the job ID and account in `docs/runs/<run>.md`.
5. Racing copies share `tml_2026`'s fair-share, so they also lower the priority of the team's other jobs. Cancel
   losers promptly.

*Decided by: the team (recorded by Mrunmay).*

### 2026-10-05: The leaderboard metric is pass@8; the gate compares Acc
The base AIME run gave Acc 0.167 (last year 0.200, one problem apart) but Pass@1 0.067 (Qwen reports ~6.7%), and
GPQA's 0.742 can't be Pass@1 for a 3B model. So last year's table, the 0.446 baseline and the 0.451/0.492 random
runs are **pass@8**. The Step 2 gate now compares Acc. Pass@1 stays the primary metric for our smart-vs-random
claim (lower variance), and `results.md` reports both metrics with a seed spread for each.

### 2026-10-05: A100 by default
The H200 queue estimated a 4-day wait for 1-GPU eval jobs. A100s are the default (`GPU=h200` to override); every
compared run should use the same GPU type.

### 2026-10-05: antlr4 4.9.3 in evalenv (main README route)
`eval/requirements.txt` pins `antlr4-python3-runtime==4.11.1` and `latex2sympy2==1.9.1`, which cannot coexist:
pip raises `ResolutionImpossible` on ARC, and under 4.11.1 latex2sympy2 can't even be imported. We follow the main
README instead: `pip install --no-deps latex2sympy2==1.9.1` with antlr4 4.9.3 (omegaconf's 4.9.x). The grader check
passes. *Decided by: Manas.*

### 2026-10-05: transformers 4.44.2 in evalenv
`transformers` is unpinned in `eval/requirements.txt` and now resolves to 5.x, which vLLM 0.6.1 predates. We pin the
release that was current alongside vLLM 0.6.1. `flash_attn` is installed after torch with `--no-build-isolation`;
eval never imports it.

### 2026-10-05: torch 2.6.0+cu126 in myenv
Unpinned torch (from LLaMA-Factory's `.[torch]` extra) now resolves to 2.14 built for CUDA 13.0. flash-attn has no
wheel for it and can't build against ARC's CUDA 12.6 module. 2.6.0+cu126 matches the module, has a prebuilt
flash-attn wheel, and is proven on these nodes. No requirement file pins torch.

### 2026-10-05: Two environments, built from the tested requirement files
`myenv` (py3.10): `LLaMA-Factory/requirements.txt` + README §1.1/1.3/1.4. `evalenv` (py3.11): `eval/requirements.txt`
(eval/README). Extra analysis packages are added only under a frozen-constraints install. *Decided by: Manas.*

### 2026-10-05: Datasets registered exactly as the README does → Qwen default system prompt in training
`{"<name>": {"file_name": "<name>.json"}}` only. With this registration LLaMA-Factory ignores the JSON's `system`
field and trains with the `qwen` template default ("You are Qwen, created by Alibaba Cloud. You are a helpful
assistant."), while eval uses "Please reason step by step, and put your final answer within \boxed{}.". This is
deliberate, identical across all runs, and overrides CLAUDE.md's original invariant. **Do not "fix" it with a
`columns` map.** *Decided by: Manas.*

### 2026-10-05: Training = the README YAML verbatim
ZeRO-3 offload, lr 5e-6, 3 epochs, bs 1 × GA 8, warmup 0, cosine, cutoff 16384, output under
`saves/qwen25_3b_instruct/`. Every comparison run uses 8 GPUs (global batch 64). The only added key is
`save_total_limit: 1`, which saves disk and doesn't change training.

### 2026-10-05: The course's LLaMA-Factory snapshot, not hiyouga main
Current hiyouga main requires Python ≥3.11, which contradicts the README's `python=3.10`. The course repo ships a
snapshot (v0.9.4.dev0), and the README's own links point to it.

### 2026-10-05: SLURM account `tml_2026`
It has A100 and H200 access (QOS `tc_a100_normal_short`, `tc_h200_normal_short`, and `tc_normal_short` for CPU jobs).
This replaces the README's `ece_6514`. *Decided by: Manas.*

### 2026-10-05: Selection design (proposal, to be confirmed with Step 4 data)
- Math only.
- Drop truncated, ungradeable, proof-like, contaminated (test + dev) and flagged rows.
- Keep pass_rate in [0, 0.5], and drop 0/8 rows that disagree with the R1 majority.
- Stratify across 100 clusters.
- One R1 response per prompt.

Any change to thresholds must be justified on the **dev set**.

### 2026-10-05: "Seed" means the subset-sampling seed
The training seed is the HF default for every run. `random_s1` vs `random_s2` measures data-sampling noise plus
training nondeterminism.

### 2026-10-09: Step 4 scores with k=4 base-model attempts per prompt, not 8
CLAUDE.md specifies k=8. With 1-GPU jobs waiting days, k=4 halves generation (about 5–12 instead of 10–25 A100
GPU-h). pass_rate then takes values 0, 0.25, 0.5, 0.75, 1, which still separates never / sometimes / always solved.
The selection rule needs only that. The "drop 0/8 rows with low R1 agreement" rule becomes "drop 0/4 rows".
`SAMPLES=8 launch/score_pool.sh` restores k=8. *Decided by: Manas.*

### 2026-10-09: vLLM CPU swap space raised in our scoring script
`scripts/score_pool_generate.py` passes `swap_space=32` (GiB; `--swap-gb`). The base OlympiadBench eval aborted with
"Aborted due to the lack of CPU swap space" at vLLM's 4 GiB default, and scoring also samples n>1 per prompt.
This affects memory only, not sampling. The frozen `eval/` is untouched; for evals the workaround is 2 GPUs (tensor parallel).

### 2026-10-10: Trained-model evals run on 2 GPUs
`launch/eval_model.sh` requests `EVAL_GPUS` GPUs per benchmark job: 1 for the base model, **2 for every trained model**.
eval.py runs tensor-parallel over every visible GPU. 2 GPUs give vLLM twice the KV cache and 8 GiB of CPU swap, which
avoids the crash seen on base OlympiadBench. `eval/` is unchanged, and so are sampling and grading. The setting is the
same for every trained run, so comparisons stay fair. Base numbers all came from 1 GPU: 1× A100 for 7 benchmarks, 1× H200 for OlympiadBench, whose 141 GB fit where 1× A100 crashed.

### 2026-10-12: Selection uses the planned design as-is (no tuning); subsets travel as row lists
Step 4 results: on 67,432 math rows, pass_rate (k=4) has median 0 and mean 0.26 (more than half are 0/4 for the 3B
model), and the median r1_agreement is 0.5 over 28,372 multi-response rows. The project is a data-selection study, so
we keep the band [0, 0.5] from the 2026-10-05 proposal rather than tuning it. The 0/4 dominance is reported as a
finding. If a quick spot-check shows the R1 disagreements are grader formatting artefacts, the R1-majority filter is
switched off rather than tuned. Only the account that holds `analysis/pool_scores.parquet` runs `select_subset.py`; it
commits `data_subsets/<name>.idx.txt` + `.meta.json`. Teammates rebuild the training JSON with
`scripts/subset_from_idx.py <name>`, which refuses to write if the sha256 differs. *Decided by: Manas.*

### 2026-10-12: Focus on the required runs; ablations are not trained
GPU queue time is the bottleneck and the deadline is Oct 20, so we train only what the deliverables need: `random_s1`,
`random_s2` (both kept: one random run can't separate a real gain from noise) and `full_method_s1` (the smart
model). `filter_only_s1` and `filter_difficulty_s1` are built and committed but **not trained**. If GPUs free up
late, `filter_only_s1` goes first. The report describes the method's components and the funnel, says the ablations were
not run for compute reasons, and doesn't attribute any gain to a specific component. *Decided by: Manas.*

