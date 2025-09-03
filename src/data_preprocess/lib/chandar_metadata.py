#!/usr/bin/python

import pandas as pd
from  src.amr_utility import name_utility
import numpy as np
from ast import literal_eval

'''
This is adapted from metadata.py for use with NCBI data

Output files and figures:
'list_strain.txt','list_temp.txt': list of all the strains in the AMR phenotype data.# To be optimized....
'genome_list': list for downloading.
'list_species.txt': list of all the species in the AMR phenotype data
'list_species_final_bq.txt': list of all the species > 500 strains in the AMR phenotype. bq: before quality control.
'list_species_final_quality.csv': list of selected species with fine quality
'Species_antibiotic_FineQuality.csv': selected antibiotics after filter. Only For visualization. 
'Number of fine quality genomes', 'number of genome','count'
'quality/GenomeFineQuality_'+str(species.replace(" ", "_"))+'.txt': fine quality genome ID w.r.t. each species.
==============
'''


def summarise_strain(temp_path):
    '''load in metadata,summerise the strain info
    Index(['genome_id', 'genome_name', 'taxon_id', 'antibiotic',
           'resistant_phenotype', 'measurement', 'measurement_sign',
           'measurement_value', 'measurement_unit', 'laboratory_typing_method',
           'laboratory_typing_method_version', 'laboratory_typing_platform',
           'vendor', 'testing_standard', 'testing_standard_year', 'source'],
          dtype='object')
    '''
    data = pd.read_csv('./data/NCBI/NCBI_genomes_AMR.txt', dtype={'genome_id': object}, sep="\t")
    # get the first column, save it in a file named genome_list
    list = data.loc[:, ("genome_id", "genome_name")]
    list = list.groupby(by="genome_id")
    summary = list.describe()
    summary.to_csv(temp_path + 'list_strain.txt', sep="\t")  # 67836 genomes strains and 99 species.


# ====================================
def summarise_species(temp_path):
    '''summarise the species info'''
    data = pd.read_csv(temp_path + 'list_strain.txt', dtype={'genome_id': object}, skiprows=2, sep="\t", header=0)
    data.columns = ['genome_id', 'count', 'unique', 'top', 'freq']
    # summarize the strains
    data['top'] = data['top'].astype(str)  # add a new column
    data['species'] = data.top.apply(lambda x: ' '.join(x.split(' ')[0:2]))
    # Note: download genome data from here, i.e. for each strain.
    data.to_csv(temp_path+'list_temp.txt', sep="\t")
    data = data.loc[:, ("genome_id", "species")]
    # make a summary by strain
    data_s = data.groupby(by="species")
    summary_species = data_s.describe()
    summary_species.to_csv(temp_path + 'list_species.txt', sep="\t")  # list of all species


# ================================================================
def sorting_deleting(N, temp_path):
    '''retain only this that has >=N strains for a specific antibiotic w.r.t. a species'''
    data = pd.read_csv(temp_path + 'list_species.txt', dtype={'genome_id': object}, skiprows=2, sep="\t", header=0)
    data = data.iloc[:, 0:2]
    data.columns = ['species', 'count']
    data = data.sort_values(by=['count'], ascending=False)  # sorting
    data = data.reset_index(drop=True)
    data.to_csv(temp_path + 'list_species_sorting.txt', sep="\t")
    data = data[data['count'] > N]  # deleting
    data.to_csv(temp_path + 'list_species_final_bq.txt', sep="\t")  # list of all species selected by 1st round.


# =================================================================
def extract_id(temp_path):
    '''extract (useful) NCBI id to genome_list
    before quality control'''
    data = pd.read_csv(temp_path + 'list_temp.txt', dtype={'genome_id': object}, sep="\t")
    df_species = pd.read_csv(temp_path + 'list_species_final_bq.txt', dtype={'genome_id': object}, sep="\t", header=0)
    species = df_species['species']
    species = species.tolist()
    # select rows that strain name belongs to the 10 in df_species
    data = data.loc[data['species'].isin(species)]
    data = data.reset_index(drop=True)
    list_download = data['genome_id']
    list_download.to_csv('./data/NCBI/meta/genome_list', sep="\t", index=False,
                         header=False)  # all the genome ID should be downloaded.



def extract_id_species(temp_path):
    '''
    extract id for each species. For generating feature, not for models(need more filter)!
    :return: txt file containing ID for each species
    '''
    data, info_species = name_utility.load_metadata(SpeciesFile=temp_path + 'list_species_final_bq.txt')# Returns the rows from NCBI_genomes_AMR.txt which correspond to the species listed in list_species_final_bq.txt
    for species in info_species:
        data_sub = data[data['species'] == species]
        data_sub_uniqueID = data_sub.groupby(by="genome_id").count()  # rm duplicates
        ID = data_sub_uniqueID.index.to_list()
        ID_kmer = pd.DataFrame(ID, columns=["genome_id"])
        # -------------
        # for prokka or kmer use. (AMRP only)
        ID_kmer.to_csv('./data/NCBI/meta/by_species_bq/id_' + str(species.replace(" ", "_")), sep="\t", index=False,
                       header=False)


