#!/bin/bash
#SBATCH --partition=long-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=8G
#SBATCH --time=12:00:00
#SBATCH --job-name=resfinder
#SBATCH --array=0-4
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A_%a.out
# 2026-11 rerun: one array task per species (or pass a species name as $1 to run a single one).
# Point-/ResFinder DBs are already KMA-indexed (AMR_software/resfinder/db_*); re-index manually with
# INSTALL.py if the DBs are ever replaced (not done here to avoid races between array tasks).
SPECIES=(Klebsiella_pneumoniae Acinetobacter_baumannii Staphylococcus_aureus Pseudomonas_aeruginosa Escherichia_coli)
BACTERIA_NAME=${1:-${SPECIES[$SLURM_ARRAY_TASK_ID]}}
echo "Date: $(date)  Host: $(hostname)  Species: $BACTERIA_NAME"

cd /home/mila/a/aselstya/scratch/amr/AMR_benchmarking
export PATH=$HOME/miniconda3/bin:$PWD/src:$PATH
export PYTHONPATH=$PWD
bash ./scripts/model/resfinder.sh "$BACTERIA_NAME"
status=$?
echo "Done: $(date) status=$status"
exit $status
