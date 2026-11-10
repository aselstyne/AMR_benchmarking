#!/bin/bash
#SBATCH --partition=long
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=32G
#SBATCH --time=1-12:00:00
#SBATCH --job-name=aytan
#SBATCH --gres=gpu:1
#SBATCH --constraint=turing|volta|ampere
#SBATCH --array=0-4
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A_%a.out
# 2026-11 rerun: one array task per species (or pass a species name as $1). Needs the ResFinder KMA
# outputs (log/software/resfinder_k) for that species. torch 1.10.2+cu113 -> no L40S/H100 (constraint).
SPECIES=(Klebsiella_pneumoniae Acinetobacter_baumannii Staphylococcus_aureus Pseudomonas_aeruginosa Escherichia_coli)
BACTERIA_NAME=${1:-${SPECIES[$SLURM_ARRAY_TASK_ID]}}
echo "Date: $(date)  Host: $(hostname)  Species: $BACTERIA_NAME"; nvidia-smi -L

cd /home/mila/a/aselstya/scratch/amr/AMR_benchmarking
export PATH=$HOME/miniconda3/bin:$PATH
bash ./scripts/model/AytanAktug_SSSA.sh "$BACTERIA_NAME"
status=$?
echo "Done: $(date) status=$status"
exit $status
