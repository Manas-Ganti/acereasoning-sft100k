# Sourced by launchers before submitting jobs that use `source activate` (eval/eval_single.sh).
#
# Root cause (ARC, 2026-10-05): the login shell has a personal ~/miniconda3 base active (conda init in
# ~/.bashrc, auto_activate: True), and sbatch --export=ALL copies that state into the job. There,
# eval_single.sh's `module load Miniconda3` prepends the module's conda dirs to PATH, and
# `source activate <env>` -- which does succeed -- only REPLACES the previously active prefix's PATH
# entries (~/miniconda3/bin, further back), leaving the module's base bin in front. Result: python is
# the module's base 3.13 while CONDA_PREFIX says evalenv.
#
# Fix: hand the job a conda-free environment. From CONDA_SHLVL=0, conda activate PREPENDS the env's
# bin, ahead of everything the module added. This only changes the launcher's own process.
clean_conda_env() {
    if command -v module &>/dev/null; then module unload Miniconda3 >/dev/null 2>&1 || true; fi
    local v
    for v in $(compgen -e | grep -E '^(CONDA_|_CE_|_CONDA_)'); do unset "$v"; done
    unset -f conda __conda_activate __conda_reactivate __conda_hashr __conda_exe 2>/dev/null || true
    PATH=$(printf '%s' "$PATH" | tr ':' '\n' | grep -v -E '/miniconda3(/|$)|/Miniconda3(/|$)|/\.conda/envs/' | paste -sd: -)
    export PATH
}
