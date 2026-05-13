#!/bin/bash
#SBATCH --partition=unkillable
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=1-00:00:00
#SBATCH --job-name=atyan-subsample
#SBATCH --gres=gpu:1
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A.out

echo "Date:     $(date)"
echo "Hostname: $(hostname)"

# Create a variable for the bacteria name
BACTERIA_NAME="Klebsiella_pneumoniae"

cd /home/mila/a/aselstya/scratch/amr/AMR_benchmarking
conda deactivate
bash ./scripts/model/AytanAktug_SSSA.sh "$BACTERIA_NAME"