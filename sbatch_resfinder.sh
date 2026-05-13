#!/bin/bash
#SBATCH --partition=long-cpu
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=1:00:00
#SBATCH --job-name=resfinder-kleb
#SBATCH --output=/home/mila/a/aselstya/scratch/amr/AMR_benchmarking/outs/%x_%A.out

echo "Date:     $(date)"
echo "Hostname: $(hostname)"

# Create a variable for the bacteria name
BACTERIA_NAME="Klebsiella_pneumoniae"

export PATH="$PWD"/src:$PATH
export PYTHONPATH=$PWD
SCRIPTPATH=$PWD

## install KMA and  Resfinder
#If issues arise in this step, you can alternatively manually install it.
# please further refer to https://bitbucket.org/genomicepidemiology/resfinder/src/master/

# cd ./AMR_software/resfinder
# cd cge
# #unzip kma.zip
# git clone https://bitbucket.org/genomicepidemiology/kma.git
# cd kma && make
# cd ${SCRIPTPATH}

### Reference database version 2021-05-06. You can also downlaoding the latest version from the ResFinder website.
# cd ./AMR_software/resfinder
# echo -e A | unzip db_pointfinder.zip
# echo -e A | unzip db_resfinder.zip
# cd ${SCRIPTPATH}

##index Point-/ResFinder databases with KMA
cd ./AMR_software/resfinder/db_resfinder
python3 INSTALL.py ${SCRIPTPATH}/AMR_software/resfinder/cge/kma/kma non_interactive
cd ${SCRIPTPATH}
cd ./AMR_software/resfinder/db_pointfinder
python3 INSTALL.py ${SCRIPTPATH}/AMR_software/resfinder/cge/kma/kma non_interactive
cd ${SCRIPTPATH}

bash ./scripts/model/resfinder.sh "$BACTERIA_NAME"