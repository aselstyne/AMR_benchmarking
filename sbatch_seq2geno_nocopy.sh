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
TMPDIR_ROOT=$SCRATCH_ROOT

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
eval $(parse_yaml Config.yaml)

export PATH="$PWD"/src:$PATH
export PYTHONPATH=$PWD
SCRIPTPATH=$TMPDIR_ROOT # The root directory


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
cd ./AMR_software/seq2geno/install/
./TESTING.sh # dry run and set Roary dependencies
conda deactivate
## Then update seq2geno to the adaption version that can deal with genomic data
cd ${SCRIPTPATH}
cd ./AMR_software/
cp  -r seq2geno_assemble/* seq2geno/
wait
source activate ${phylo_name} #install R packages

Rscript --vanilla ${SCRIPTPATH}/install/phylo_env.r
conda deactivate
cd ${SCRIPTPATH}
bash ./scripts/model/seq2geno.sh #Run.
