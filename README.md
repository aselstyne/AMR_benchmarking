# Chandar AMR Benchmarking
Adapted to support NCBI data. For the full readme from the existing repo, see README-patric-version.md.

## Steps to Get Running:
### 1. Update variables
Config.yaml comes from the parent repository and has a variety of variables. 
- Section A can mostly be left alone for our purposes.
- Ensure that none of the listed conda env names in section "B" conflict with any you already have. If so, change the values in Config.yaml before proceeding.
- Section C is where you specify which species you want to run the baselines on. Update as you please. The selected species must be present in `data/NCBI/meta/loose_Species_antibiotic_FineQuality.csv`. If you want to limit the drugs tested, change the content of that file. Some species/drugs are not included in the file as they did not meet the minimum 200 samples threshold.
- The NCBI specific values at the end of the file need to be updated to match your values from the hydra config in our `amr_pred` repo. These values are used to preprocess the dataset to match the PATRIC format.

### 2. Install conda environments
From the root of the repository (which you will need as your working directory for all the other scripts as well), run `bash ./install/install.sh`. This should create the 9 new conda environments. Ensure there are no errors in installation. Pytorch needs to be installed manually in the `multi_torch_env`, simply activate the environment and `pip3 install torch torchvision` (for the Mila cluster, with GPU support).

### 3. NCBI data preprocessing
*Ensure you have all conda environments deactivated before running any scripts*

Run `bash NCBI_preprocess.sh`. This will create a folder of symlinks to the FASTA files, and create/populate `data/NCBI`. You may run into directory-creating errors in execution (exist_okay=False type of errors), so create the directories manually if needed. Otherwise it should run as expected.

### 4. Additional dependencies
- You must install [kma](https://bitbucket.org/genomicepidemiology/kma.git) with: 
    ```
    cd AMR_software/resfinder/cge
    git clone https://bitbucket.org/genomicepidemiology/kma.git
    cd kma && make
    ```
- (From PATRIC README, I have not tested this) For Kover, please refer to [Kover](https://aldro61.github.io/kover/doc_installation.html) to try other installation methods.

### 5. Run baselines
To run the baselines, use `bash main.sh`. This file runs scripts from the `scripts` directory in sequence, one for each baseline. Several methods rely on resfinder_k, so you need to run resfinder first.
