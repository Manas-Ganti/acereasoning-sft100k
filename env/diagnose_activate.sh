#!/bin/bash
# Why does `source activate <env>` not switch interpreters on ARC? (eval_single.sh relies on it.)
#   bash env/diagnose_activate.sh [env]   -- paste the whole output
E="${1:-evalenv}"
module load Miniconda3 >/dev/null 2>&1
P=$(conda env list | awk -v e="$E" '$1==e {print $NF}')
echo "conda: $(conda --version)   env $E -> $P"
echo "module is a: $(type -t module)   activate script: $(command -v activate)"
echo "--- 1. source activate <name> (stderr shown)"
bash -c "module load Miniconda3 >/dev/null 2>&1; source activate $E; echo \"rc=\$? CONDA_PREFIX=\$CONDA_PREFIX\"; command -v python"
echo "--- 2. source activate <absolute path>"
bash -c "module load Miniconda3 >/dev/null 2>&1; source activate $P; echo \"rc=\$? CONDA_PREFIX=\$CONDA_PREFIX\"; command -v python"
echo "--- 3. PATH pinned, then module load only (does module load re-prepend base?)"
PATH="$P/bin:$PATH" bash -c "module load Miniconda3 >/dev/null 2>&1; command -v python; echo \"\$PATH\" | tr : '\n' | head -4"
echo "--- 4. PATH pinned, module load, source activate <name>"
PATH="$P/bin:$PATH" bash -c "module load Miniconda3 >/dev/null 2>&1; source activate $E; command -v python; echo \"\$PATH\" | tr : '\n' | head -4"
echo "--- 5. conda shell hook + conda activate"
bash -c "module load Miniconda3 >/dev/null 2>&1; eval \"\$(conda shell.bash hook)\"; conda activate $E; command -v python"
