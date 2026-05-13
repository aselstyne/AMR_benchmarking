#!/bin/bash
#SBATCH --partition=main-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=2-00:00:00
#SBATCH --job-name=seq2geno-kleb
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A.out

echo "Date:     $(date)"
echo "Hostname: $(hostname)"

# Create a variable for the bacteria name
BACTERIA_NAME="Klebsiella_pneumoniae"

# Create a variable for the scratch root directory
SCRATCH_ROOT="/home/mila/a/aselstya/scratch/amr/AMR_benchmarking"
TMPDIR_ROOT="$SLURM_TMPDIR/AMR_benchmarking"

echo "Starting directory copy to compute node... (This will take roughly 10-15 mins)"
mkdir -p $TMPDIR_ROOT

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
echo "Copied Config.yaml"
rsync -a --mkpath $SCRATCH_ROOT/install/ $TMPDIR_ROOT/install
echo "Copied install/"

echo "Directory copy to compute node completed. Now listing the directory structure on the compute node:"
ls -R $TMPDIR_ROOT
echo "------------------------------"

# rsync -a --mkpath \
#     $SCRATCH_ROOT/Results \
#     $SCRATCH_ROOT/AMR_software \
#     $SCRATCH_ROOT/scripts \
#     $SCRATCH_ROOT/data \
#     $SCRATCH_ROOT/ncbi_genome \
#     $SCRATCH_ROOT/src \
#     $SCRATCH_ROOT/Config.yaml \
#     $TMPDIR_ROOT/

# rsync -a --mkpath $SCRATCH_ROOT/log/software/seq2geno $TMPDIR_ROOT/log/software/seq2geno

echo "Directory copied to compute node. Completed at $(date)."




### NOW RUN THE SOFTWARE ###
cd $TMPDIR_ROOT
function parse_yaml {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\):|\1|" \
        -e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}
eval $(parse_yaml Config-tmp.yaml)

export PATH="$PWD"/src:$PATH
export PYTHONPATH=$PWD
SCRIPTPATH=$TMPDIR_ROOT


###############################
##5. Software 3.Seq2Geno2Pheno
###############################
## set up snakemake pipeline.
cd ${SCRIPTPATH}
cd ./AMR_software/seq2geno/install/
./SETENV.sh ${se2ge_env_name}
echo "Seq2Geno main env set up. Now proceed to set up denovo envs.."
export PATH=$( dirname $( dirname $( /usr/bin/which conda ) ) )/bin:$PATH
export PYTHONPATH=$PWD
source activate ${se2ge_env_name}
wait
cd ${SCRIPTPATH}
cd ./AMR_software/seq2geno/install/ ### THIS HAS A LINE COMMENTED
./TESTING.sh # dry run and set Roary dependencies
conda deactivate
## Then update seq2geno to the adaption version that can deal with genomic data
cd ${SCRIPTPATH}
cd ./AMR_software/
cp  -r seq2geno_assemble/* seq2geno/
wait
source activate ${phylo_name} #install R packages
Rscript --vanilla ./install/phylo_env.r
conda deactivate
cd ${SCRIPTPATH}
bash ./scripts/model/seq2geno.sh #Run.




### COPY BACK RESULTS TO SCRATCH ###
echo "Copying results back to original directory at $(date)."
# Copy the "Results" and "log/software/seq2geno/BACTERIA_NAME" back to the origional directory
rsync -a -P --mkpath $TMPDIR_ROOT/Results/software/seq2geno/ $SCRATCH_ROOT/Results/software/seq2geno
rsync -a -P --mkpath $TMPDIR_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME/ $SCRATCH_ROOT/log/software/seq2geno/software_output/$BACTERIA_NAME

echo "Results copied back to original directory."
