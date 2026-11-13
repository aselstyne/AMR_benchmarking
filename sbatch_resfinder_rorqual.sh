#!/bin/bash
#SBATCH --account=rrg-bengioy-ad_cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=16G
#SBATCH --time=3:00:00
#SBATCH --job-name=resfinder
#SBATCH --array=0-3
#SBATCH --output=/scratch/styne/amr/AMR_benchmarking/outs/%x_%A_%a.out
# 2026-11 rerun, Rorqual copy: only the per-genome Point-/ResFinder runs (blastn + KMA versions).
# Outputs land in log/software/resfinder_{b,k}/software_output/<Species>/ and are rsynced back to Mila,
# where extract_results.py scoring and Aytan-Aktug run. Kleb is not here: its outputs already exist on Mila.
SPECIES=(Acinetobacter_baumannii Staphylococcus_aureus Pseudomonas_aeruginosa Escherichia_coli)
SP=${1:-${SPECIES[$SLURM_ARRAY_TASK_ID]}}
echo "Date: $(date)  Host: $(hostname)  Species: $SP"
cd /scratch/styne/amr/AMR_benchmarking
module -q load StdEnv/2023 python/3.11
source .venv_res/bin/activate
module -q load blast+/2.14.1   # after venv activation (activate resets PATH)
export PYTHONPATH=$PWD
N=${SLURM_CPUS_PER_TASK:-4}
python ./AMR_software/resfinder/main_run_blastn.py -path_sequence $PWD/ncbi_genome -temp ./ --n_jobs $N -s "${SP//_/ }" -l loose || exit 1
python ./AMR_software/resfinder/main_run_kma.py    -path_sequence $PWD/ncbi_genome -temp ./ --n_jobs $N -s "${SP//_/ }" -l loose || exit 1
# Count genomes still lacking output (ResFinder errors are only printed, not raised)
for v in b k; do
  miss=0; while read g; do [ -f log/software/resfinder_$v/software_output/$SP/$g/pheno_table.txt ] || miss=$((miss+1)); done < data/NCBI/meta/by_species_bq/id_$SP
  echo "resfinder_$v $SP missing outputs: $miss"
done
echo "Done: $(date)"
