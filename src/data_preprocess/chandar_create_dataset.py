### Generate the NCBI_genomes_AMR.txt, equivalent to PATRIC_genomes_AMR.txt, by amalgamating all SRND.csv files ###

import pandas as pd
import os
from pathlib import Path
import argparse

PATH_DATASETS_REINTERPRETED = "../datasets" # Root folder, with one subfolder per species inside. Should have one CSV in each
PATH_OUT = "./data/NCBI"

def create_dataset_NCBI():
    # Search all subfolders for SR_filt.csv files
    csv_files = list(Path(PATH_DATASETS_REINTERPRETED).glob('**/*SR_filt.csv'))
    print(f"Found {len(csv_files)} CSV files.")

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

    if not mega_df.empty:
        mega_df.to_csv(f"{PATH_OUT}/NCBI_genomes_AMR.txt", sep="\t", index=False)
        print("NCBI_genomes_AMR.txt created successfully.")


def create_quality_files():
    ''' Generate dummy quality files to bypass the quality filtering steps of the pipeline'''
    # Check if the quality subfolder already exists, if not create it
    os.makedirs(f"{PATH_OUT}/quality", exist_ok=True)

    # Load the NCBI_genomes_AMR.txt file
    df = pd.read_csv(f"{PATH_OUT}/NCBI_genomes_AMR.txt", sep="\t")
    
    # Define headings and values for top quality, to bypass filtering
    headings = ["genome.genome_id", "genome.genome_name", "genome.genome_status", "genome.genome_length", "genome.genome_quality", "genome.plasmids", "genome.contigs", "genome.fine_consistency", "genome.coarse_consistency", "genome.checkm_completeness", "genome.checkm_contamination"]
    values = [0, "placeholder", "WGS", 0, "Good", 0, 5, 100, 100, 100, 0]

    # Get a list of all different species in the dataset
    species = df['genome_name'].unique()

    # Create a quality dataset for each species
    for sp in species:
        sp_df = df[df['genome_name'] == sp].copy()
        # Create a new dataframe with the new headings
        quality_df = pd.DataFrame(columns=headings)
        for row in sp_df.itertuples(index=False):
            new_row = {heading: value for heading, value in zip(headings, values)}
            new_row['genome.genome_id'] = row.genome_id
            new_row['genome.genome_name'] = row.genome_name
            quality_df = quality_df.append(new_row, ignore_index=True)
        
        # Save the quality dataset to a file
        quality_df.to_csv(f"{PATH_OUT}/quality/{sp}.csv", sep="\t", index=False)
        print(f"{sp}.csv created successfully.")

if __name__ == "__main__":
    # Add argument to override PATH_DATASETS_REINTERPRETED
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_datasets_reinterpreted", default=PATH_DATASETS_REINTERPRETED)
    args = parser.parse_args()
    PATH_DATASETS_REINTERPRETED = args.path_datasets_reinterpreted

    # Run main script
    create_dataset_NCBI()
    create_quality_files()
