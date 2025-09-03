### COPIED FROM INSTALL.SH ###
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
export PATH=$( dirname $( dirname $( which conda ) ) )/bin:$PATH
export PYTHONPATH=$PWD
##############################


# Remove the conda environments created by the install script
conda env remove -n ${amr_env_name} 
conda env remove -n ${amr_env_name2}
conda env remove -n ${resfinder_env} #3
conda env remove -n ${PhenotypeSeeker_env_name}
conda env remove -n ${multi_env_name}
conda env remove -n ${multi_torch_env_name} #6
conda env remove -n ${kover_env_name}
conda env remove -n ${phylo_name}
conda env remove -n ${kmer_env_name} #9
conda env remove -n ${phylo_name2} # NOT INSTALLED