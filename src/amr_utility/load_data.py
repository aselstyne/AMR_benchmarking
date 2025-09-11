#!/usr/bin/python

### THIS IS THE NCBI VERSION. See load_data_OLD.py for the PATRIC version ###
import pandas as pd
import numpy as np
import ast
from src.amr_utility import name_utility as name_utility
#import name_utility



def check_balance(data_sub_anti):
    '''
    :return: balance_check: the distribution of R, S phenotype.
    '''
    #todo : This is just for those inbalance data downsampling. So far, we do not include this.
    balance_check = data_sub_anti.groupby(by="resistant_phenotype").count()
    balance_ratio = balance_check.iloc[0]['genome_id'] / balance_check.iloc[1]['genome_id']

    if balance_ratio > 2 or balance_ratio < 0.5:  # #final selected, need to downsample.

        label_down = balance_check.idxmax().to_numpy()[0]
        label_keep = balance_check.idxmin().to_numpy()[0]

        data_draw = data_sub_anti[data_sub_anti['resistant_phenotype'] == label_down]
        data_left = data_sub_anti[data_sub_anti['resistant_phenotype'] != label_down]

        data_drew = data_draw.sample(n=int(1.5 * balance_check.loc[label_keep, 'genome_id']))
        data_sub_anti_downsampling = pd.concat([data_drew, data_left], ignore_index=True, sort=False)
        balance_check = data_sub_anti_downsampling.groupby(by="resistant_phenotype").count()

    else:
        data_sub_anti_downsampling=data_sub_anti

    return balance_check,data_sub_anti_downsampling

def model(species,antibiotics,balance,level):
    '''
    antibiotics_selected: antibiotics list for each species
    ID_list: sample name matrix. n_anti* n_SampleName. in the order of model/loose/Data_s_anti
    Y:  n_anti* [pheno]
    '''
    # From ALEX:
    # The function is passed in a species name
    antibiotics_selected = ast.literal_eval(antibiotics)
    ID_list=[]
    Y=[]
    for anti in antibiotics_selected:

        save_name_modelID=name_utility.GETname_meta(species,anti,level) # Get the file name
        # Load table that has the relevant genome IDs and the phenotypes for each
        data_sub_anti = pd.read_csv(save_name_modelID + '_pheno.txt', index_col=0, dtype={'genome_id': object,'resistant_phenotype':int}, sep="\t")
        data_sub_anti = data_sub_anti.drop_duplicates()#should no duplicates. Just in case.


        if balance==True:
            balance_check,data_sub_anti=check_balance(data_sub_anti)
            print('Check phenotype balance after downsampling.', balance_check)

        ID_sub_anti=data_sub_anti.genome_id.to_list()
        ID_list.append(ID_sub_anti)
        y = data_sub_anti['resistant_phenotype']
        y = np.array(y)
        Y.append(y)
    return antibiotics_selected,ID_list,Y

def extract_info(s,balance,level):
    ''' s (list of species), balance (bool), and level (string, usually "loose")
    returns:
    - antibiotics (list of all relevant antibiotics for this species)
    - ID_list (list of lists; one sublist per antibiotic; each sublist contains the relevant assembly IDs)
    - Y (related list of lists; each sublist contains the labels (0 for susceptible, 1 for resistant) for each assembly ID)'''

    main_meta,_=name_utility.GETname_main_meta(level)
    data = pd.read_csv(main_meta, index_col=0,dtype={'genome_id': object}, sep="\t")
    data = data[data['number'] != 0]# drop the species with 0 in column 'number'.
    data = data.loc[[s], :]
    #data.at['Mycobacterium tuberculosis', 'modelling antibiotics']=['capreomycin', 'ciprofloxacin']
    # --------------------------------------------------------
    df_species = data.index.tolist()
    antibiotics = data['modelling antibiotics'].tolist()

    for df_species,antibiotics in zip(df_species, antibiotics):
        # The df appears to be of length 1 most of the time at least
        antibiotics, ID_list, Y=model(df_species, antibiotics,balance,level)

    return antibiotics,ID_list,Y

if __name__ == "__main__":
    main_meta,_=name_utility.GETname_main_meta("loose")
    data = pd.read_csv(main_meta, index_col=0, dtype={'genome_id': object}, sep="\t") 
    df_species = data.index.tolist() # This is a dataframe of 3 columns: species name, number of applicable drugs, list of applicable drugs.

    for species in df_species[:1]:

        antibiotics, ID_list, Y =  extract_info(species, False, "loose")
        print(antibiotics)
        print(ID_list)
        print(len(Y))
