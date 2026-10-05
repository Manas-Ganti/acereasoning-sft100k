#!/bin/bash
#SBATCH --job-name=test-activation
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:05:00
# Reproduces eval/eval_single.sh's environment lines EXACTLY (module loads, then
# `source activate ${CONDA_ENV:-myenv}`, then a bare `python`), for CONDA_ENV given as a bare
# name and as an absolute path. sys.executable is the evidence, not conda's own report.
#   launch/test_activation.sh
for CONDA_ENV in evalenv "$HOME/.conda/envs/evalenv" myenv "$HOME/.conda/envs/myenv"; do
    echo "=================== CONDA_ENV=$CONDA_ENV"
    (
        if command -v module &> /dev/null; then
            module load Miniconda3
            module load CUDA/12.6.0
        fi
        source activate ${CONDA_ENV:-myenv}
        echo "source activate rc=$?"
        echo "command -v python: $(command -v python)"
        python -V 2>&1 || echo "python -V failed"
        python -c "import sys; print('sys.executable:', sys.executable)"
        case "$CONDA_ENV" in
            *evalenv) python -c "import vllm; from latex2sympy2 import latex2sympy; print('evalenv sentinel OK, vllm', vllm.__version__)" 2>&1 | grep -v -i "libcuda\|ANTLR" ;;
            *myenv)   python -c "import llamafactory, transformers; print('myenv sentinel OK, transformers', transformers.__version__)" 2>&1 | tail -1 ;;
        esac
    )
done
