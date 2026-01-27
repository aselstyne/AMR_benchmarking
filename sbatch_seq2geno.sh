#!/bin/bash
#SBATCH --partition=long-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=5-00:00:00
#SBATCH --job-name=seq2geno-kleb
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A.out

# Echo time and hostname into log
echo "Date:     $(date)"
echo "Hostname: $(hostname)"

# Create a variable for the bacteria name
BACTERIA_NAME="Klebsiella_pneumoniae"

# Create a variable for the scratch root directory
SCRATCH_ROOT="/home/mila/a/aselstya/scratch/amr/AMR_benchmarking"
TMPDIR_ROOT="$SLURM_TMPDIR/AMR_benchmarking"

# Copy the critical parts of the AMR_benchmarking directory to the compute node
echo "Starting directory copy to compute node... (This will take roughly 10 mins)"
rsync -a --mkpath $SCRATCH_ROOT/log/software/seq2geno/ $TMPDIR_ROOT/log/software/seq2geno
echo "Copied log/software/seq2geno/"
rsync -a --mkpath $SCRATCH_ROOT/Results/ $TMPDIR_ROOT/Results
echo "Copied Results/"
rsync -a --mkpath $SCRATCH_ROOT/AMR_software/seq2geno/ $TMPDIR_ROOT/AMR_software/seq2geno
echo "Copied AMR_software/seq2geno/"
rsync -a --mkpath $SCRATCH_ROOT/AMR_software/seq2geno_assemble/ $TMPDIR_ROOT/AMR_software/seq2geno_assemble
echo "Copied AMR_software/seq2geno_assemble/"
rsync -a --mkpath $SCRATCH_ROOT/scripts/model/seq2geno.sh $TMPDIR_ROOT/scripts/model/seq2geno.sh
echo "Copied scripts/model/seq2geno.sh"
rsync -a --mkpath $SCRATCH_ROOT/data/ $TMPDIR_ROOT/data
echo "Copied data/"
rsync -a --mkpath $SCRATCH_ROOT/ncbi_genome/ $TMPDIR_ROOT/ncbi_genome
echo "Copied ncbi_genome/"
rsync -a --mkpath $SCRATCH_ROOT/src/ $TMPDIR_ROOT/src
echo "Copied src/"
rsync -a $SCRATCH_ROOT/Config.yaml $TMPDIR_ROOT

echo "Directory copied to compute node. Completed at $(date)."

cd $TMPDIR_ROOT
# bash ./scripts/model/seq2geno.sh "$BACTERIA_NAME"
mkdir -p $TMPDIR_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME/
echo "Test file" > $TMPDIR_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME/test_output.txt


echo "Copying results back to original directory at $(date)."
# Copy the "Results" and "log/software/seq2geno/BACTERIA_NAME" back to the origional directory
rsync -a -P --mkpath $TMPDIR_ROOT/Results/software/seq2geno/ $SCRATCH_ROOT/Results/software/seq2geno
rsync -a -P --mkpath $TMPDIR_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME/ $SCRATCH_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME

echo "Results copied back to original directory."