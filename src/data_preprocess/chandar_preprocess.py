#!/usr/bin/python
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import logging,argparse
import lib.chandar_metadata, lib.chandar_summary, lib.chandar_metadata_multi_model, lib.chandar_quality
from  src.amr_utility import file_utility
from src.amr_utility import name_utility
import pandas as pd

def workflow(level,logfile,temp_path):
    handlers = [
        logging.StreamHandler()
    ]
    if logfile is not None:
        handlers.append(logging.FileHandler(logfile, mode='w'))
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers

    )

    logger = logging.getLogger('data_preprocess')

    ###  1. Filtering species and antibiotics by genome number
    temp_path=temp_path+'log/temp/data/'
    file_utility.make_dir(temp_path)
    lib.chandar_metadata.summarise_strain(temp_path)
    logger.info('finish extracting information from NCBI_genomes_AMR.txt')
    lib.chandar_metadata.summarise_species(temp_path)
    lib.chandar_metadata.sorting_deleting(100,temp_path) #100: retain only this that has >=100 strains for a specific antibotic w.r.t. a species
    lib.chandar_metadata.extract_id(temp_path)
    lib.chandar_metadata.extract_id_species(temp_path)


    ### 2. genome quality control
    # Quality is considered to already be controlled for with the NCBI data, and we don't have the right attributes for it anyway.
    lib.chandar_quality.extract_id_quality(temp_path,level)
    lib.chandar_quality.filter_phenotype(level,False) #False indicates No extra sampling handling for imbalance dataset.

    ### 3. get genome number. Print to the console.
    lib.chandar_summary.summary_genome(level)

    ### 4. get genome number per combination. Save to ./data/NCBI/meta/'+str(level)+'_genomeNumber/
    file_utility.make_dir('./data/NCBI/meta/'+str(level)+'_genomeNumber')
    main_meta,_= name_utility.GETname_main_meta(level)
    data = pd.read_csv(main_meta, index_col=0, dtype={'genome_id': object}, sep="\t")
    data = data[data['number'] != 0]
    df_species = data.index.tolist()
    for species  in  df_species :
        lib.chandar_summary.summary_pheno(species,level)


    ### 5. multi-species model metadata 
    lib.chandar_metadata_multi_model.extract_multi_model_summary(level)
    ## get genome number for each of species-antibiotic combination in multi-species-antibiotic dataset. save it to file.  Sep 2023
    lib.chandar_metadata_multi_model.extract_multi_model_size(level)



if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--level', default='loose', type=str, required=False,
                        help='Quality control: strict or loose.default=\'loose\'.')
    parser.add_argument( '--logfile', default=None, type=str, required=False,
                        help='The log file')
    parser.add_argument('-temp', '--temp_path', default='./', type=str, required=False,
                        help='The log file')
    parsedArgs=parser.parse_args()
    workflow(parsedArgs.level,parsedArgs.logfile,parsedArgs.temp_path)
