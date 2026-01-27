### Generate the NCBI_genomes_AMR.txt, equivalent to PATRIC_genomes_AMR.txt, by amalgamating all SRND.csv files ###

import pandas as pd
import os
from pathlib import Path
import argparse
import json

PATH_DATASETS_REINTERPRETED = "../datasets" # Root folder, with one subfolder per species inside. Should have one CSV in each
PATH_OUT = "./data/NCBI"

def create_dataset_NCBI():
    # Search all subfolders for SR_filt.csv files
    csv_files = list(Path(PATH_DATASETS_REINTERPRETED).glob('**/*SR_filt.csv'))
    print(f"Found {len(csv_files)} CSV files, combining...")

    if not csv_files:
        print("No CSV files found. Exiting.")
        exit()

    # Read and concatenate all CSV files
    mega_df = pd.DataFrame()
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        mega_df = pd.concat([mega_df, df], ignore_index=True)
    
    # Adjust the headings and columns of the data.
    # Target columns: ['genome_id', 'genome_name', 'antibiotic', 'resistant_phenotype']
    # Source columns: ['Assembly', 'Organism group', 'Antibiotic', 'Phenotype_revised']
    column_mapping = {
        'Assembly': 'genome_id',
        'Organism group': 'genome_name',
        'Antibiotic': 'antibiotic',
        'Phenotype_revised': 'resistant_phenotype'
    }

    # Rename and drop all other columns
    mega_df.rename(columns=column_mapping, inplace=True)
    mega_df = mega_df[list(column_mapping.values())]

    # Capitalize the first letter of each genome_name, and replace underscores with spaces
    mega_df['genome_name'] = mega_df['genome_name'].str.replace('_', ' ').str.capitalize()

    # Drop "GCA_" from the start of all genome_id entries
    mega_df['genome_id'] = mega_df['genome_id'].str.replace('GCA_', '')

    if not mega_df.empty:
        mega_df.to_csv(f"{PATH_OUT}/NCBI_genomes_AMR.txt", sep="\t", index=False)
        print("NCBI_genomes_AMR.txt created successfully.")


def create_quality_files():
    ''' Generate dummy quality files to bypass the quality filtering steps of the pipeline'''
    print("\nGenerating dummy quality files...")
    # Check if the quality subfolder already exists, if not create it
    os.makedirs(f"{PATH_OUT}/quality", exist_ok=True)

    # Load the NCBI_genomes_AMR.txt file, keeping leading zeros in genome_id
    df = pd.read_csv(f"{PATH_OUT}/NCBI_genomes_AMR.txt", sep="\t", dtype=str)

    # Define headings and values for top quality, to bypass filtering
    # headings = ["genome.genome_id", "genome.genome_name", "genome.genome_status", "genome.genome_length", "genome.genome_quality", "genome.plasmids", "genome.contigs", "genome.fine_consistency", "genome.coarse_consistency", "genome.checkm_completeness", "genome.checkm_contamination"]
    # values = [0, "placeholder", "WGS", 0, "Good", 0, 5, 100, 100, 100, 0]
    headings = ["genome.genome_status", "genome.genome_length", "genome.genome_quality", "genome.plasmids", "genome.contigs", "genome.fine_consistency", "genome.coarse_consistency", "genome.checkm_completeness", "genome.checkm_contamination"]
    values = ["WGS", 0, "Good", 0, 5, 100, 100, 100, 0]

    # Get a list of all different species in the dataset
    species = df['genome_name'].unique()

    # Create a quality dataset for each species
    for sp in species:
        sp_df = df[df['genome_name'] == sp].copy()
        # drop columns "antibiotic" and "resistant_phenotype"
        sp_df = sp_df.drop(columns=['antibiotic', 'resistant_phenotype'])
        # drop duplicate rows based on genome_id
        sp_df = sp_df.drop_duplicates(subset=['genome_id'])
        # add prefix "genome." to the column names
        sp_df = sp_df.rename(columns=lambda x: f"genome.{x}")

        # add the quality columns with the predefined values
        for heading, value in zip(headings, values):
            sp_df[heading] = value

        # Create a new dataframe with the new headings
        # quality_df = pd.DataFrame(columns=headings)
        # for row in sp_df.itertuples(index=False):
        #     new_row = {heading: value for heading, value in zip(headings, values)}
        #     new_row['genome.genome_id'] = row.genome_id
        #     new_row['genome.genome_name'] = row.genome_name
        #     quality_df = quality_df.append(new_row, ignore_index=True)
        
        # Save the quality dataset to a file
        sp_df.to_csv(f"{PATH_OUT}/quality/{sp.replace(' ', '_')}.csv", sep="\t", index=False)
        print(f"{sp.replace(' ', '_')}.csv created successfully.")

def create_cv_folds():
    ''' Translate our existing phylogeny-based CV folds to their format '''
    # Get a list of all the existing CV fold files
    cv_files = list(Path(PATH_DATASETS_REINTERPRETED).glob('**/*phyloFolds_hierarchical.csv'))
    print(f"Found {len(cv_files)} CV fold files, translating...")

    for cv_file in cv_files:
        # Extract species name and drug name
        species_name = cv_file.stem.split("__")[0].capitalize()
        drug_name = cv_file.stem.split("__")[1]
        out_file = Path(f"{PATH_OUT}/cv_folds/loose/single_S_A_folds/{species_name}/{drug_name}_phylotree_cv.json")
        os.makedirs(out_file.parent, exist_ok=True)

        # Read the CV fold file, two columns: assembly and fold
        df = pd.read_csv(cv_file)
        print(species_name, drug_name)

        # Create list of all genome ids for each fold, removing the "GCA_" prefix if present
        df['assembly'] = df['assembly'].str.replace('GCA_', '')
        folds = []
        phylo_genomes = set()
        for fold_num in df['fold'].unique():
            assembly_list = df[df['fold'] == fold_num]['assembly'].tolist()
            folds.append(assembly_list)
            phylo_genomes.update(assembly_list)
        
        # Load the generated random CV folds
        rand = json.load(open(f"{out_file.parent}/{drug_name}_random_cv.json"))
        # Create a list of all the genome ids in the random folds
        rand_genomes = set()
        for fold in rand:
            rand_genomes.update(list(fold))
        
        # Get a list of all missing genomes from either set
        in_phylo_not_rand = phylo_genomes - rand_genomes
        in_rand_not_phylo = rand_genomes - phylo_genomes
        # Remove all genomes that are in phylo but not in rand from the phylo folds
        for genome in in_phylo_not_rand:
            # Simply remove it from the folds list
            for fold in folds:
                if genome in fold:
                    fold.remove(genome)
                    break
        
        # handle the opposite case a little more delicately; warn the user and add them to the smallest fold
        for genome in in_rand_not_phylo:
            # Find the smallest fold
            smallest_fold = min(folds, key=len)
            smallest_fold.append(genome)
            print(f"Added {genome} to phylo folds, as it was not there before")

        # Check that random and phylo folds now contain the same genomes
        phylo_genomes = set()
        for fold in folds:
            phylo_genomes.update(fold)
        if phylo_genomes != rand_genomes:
            print("error: folds do not contain the same genomes after adjustment")
            exit()

        # Save the folds to a JSON file
        with open(out_file, 'w') as f:
            json.dump(folds, f)

if __name__ == "__main__":
    # Add argument to override PATH_DATASETS_REINTERPRETED
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_datasets_reinterpreted", default=PATH_DATASETS_REINTERPRETED)
    args = parser.parse_args()
    PATH_DATASETS_REINTERPRETED = args.path_datasets_reinterpreted

    # Create the output directory if it doesn't exist
    os.makedirs(PATH_OUT, exist_ok=True)
    os.makedirs(f"{PATH_OUT}/meta", exist_ok=True)
    os.makedirs(f"{PATH_OUT}/quality", exist_ok=True)
    os.makedirs(f"{PATH_OUT}/cv_folds", exist_ok=True)
    os.makedirs(f"{PATH_OUT}/cv_folds/loose", exist_ok=True)
    os.makedirs(f"{PATH_OUT}/cv_folds/loose/single_S_A_folds", exist_ok=True)
    # Run main script
    # create_dataset_NCBI()
    # create_quality_files()
    create_cv_folds()
