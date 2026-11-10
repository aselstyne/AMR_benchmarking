#!/bin/bash
#SBATCH --job-name=install-envs
#SBATCH --partition=main-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=3:00:00
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A.out

# Recreate the conda envs needed for the ResFinder + Aytan-Aktug baselines (2026-11 rerun).
# Follows install/install.sh, minus envs not needed and without editing ~/.condarc.
cd /home/mila/a/aselstya/scratch/amr/AMR_benchmarking
source $HOME/miniconda3/etc/profile.d/conda.sh
set -x
have() { conda env list | awk '{print $1}' | grep -qx "$1"; }

have amr_env || conda env create -n amr_env -f ./install/amr_env.yml || exit 1
have res_env || conda env create -n res_env -f ./install/res_env.yml || exit 1

if ! have multi_env; then
  conda create -n multi_env -y python=3.6 || exit 1
  conda activate multi_env
  pip install -r install/multi_env.txt || exit 1
  pip install torch==1.10.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html || exit 1
  conda deactivate
fi

if ! have multi_torch_env; then
  conda create -n multi_torch_env -y python=3.6 || exit 1
  conda activate multi_torch_env
  pip install -r install/multi_env.txt || exit 1
  # cu113 build: last torch for py3.6; runs on V100/RTX8000/A100 (not L40S/H100)
  pip install torch==1.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html || exit 1
  conda deactivate
fi

for e in amr_env res_env multi_env multi_torch_env; do
  conda run -n $e python -c "import sys, numpy, pandas; print('$e', sys.version.split()[0], numpy.__version__, pandas.__version__)" || exit 1
done
conda run -n amr_env python -c "import sympy, sklearn; print('amr_env sympy', sympy.__version__)" || exit 1
conda run -n res_env bash -c "blastn -version | head -1; python -c 'import cgecore'" || exit 1
conda run -n multi_torch_env python -c "import torch, sklearn; print('torch', torch.__version__, torch.version.cuda)" || exit 1
echo ENVS_OK
