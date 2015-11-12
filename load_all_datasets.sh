#!/bin/bash

# Shell script to populate D-PLACE models with data from CSV files
# CSV files are in a private Bitbucket repository under the NESCent organization
# Should be run after activating virtualenv

# Make sure that the console accepts UTF-8 (which is the default on MacOSX but NOT on any other
# UNIX systems since the debug info can contain non-ASCII characters)
export LC_ALL="en_US.UTF-8"

BASEDIR=$(dirname $0)

REPO_SRC="git@bitbucket.org:nescent/dplace-datasets.git"
REPO_DEST="${BASEDIR}/datasets"

DPLACE_PATH="${BASEDIR}"

## Clone the repository
if [ ! -d "$REPO_DEST" ]; then
	mkdir -p "$REPO_DEST"
	git clone $REPO_SRC $REPO_DEST
else
  orig=`pwd`
  cd $REPO_DEST && git pull && cd "$orig"
fi

## import the data

export DJANGO_SETTINGS_MODULE=dplace.settings
export PYTHONPATH=$DPLACE_PATH

#echo "Loading ISO Codes from Ethnologue"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" iso
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" iso

#echo "Loading ISO Code Lat/Long"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/iso_lat_long.csv" iso_lat_long

#echo "Loading Glottolog Languages"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/glottolog_mapping.csv" glotto

#echo "Loading Languages from Ethnologue"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" langs
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" langs

#echo "Loading EA Societies"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_langs+isocodes.csv" ea_soc

#echo "Loading EA Society and XD ID links"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EA_soc_id_to_xd_id_10Nov2015.csv" ea_soc_xd_id

#echo "Linking Societies to Glottocodes"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/xd_id_to_language_9Nov2015.csv" xd_lang

#echo "Loading Binford Societies"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_langs+isocodes.csv" bf_soc

#echo "Loading Binford Harmonized Societies"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_harm.csv" bf_harm

#echo "Loading Environmental Data"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.07Mar14.csv" "env_vars"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.07Mar14.csv" "env_vals"

echo "Loading EA Variables"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_variable_names+categories.csv" ea_vars
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/VariableList_10Nov2015.csv" vars

echo "Loading EA Variable Codes"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_codes.csv" ea_codes
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/CodeDescriptions_10Nov2015.csv" ea_codes

#echo "Loading EA Variable Values"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_vals.csv" ea_vals
echo "Loading EA Stacked Data"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EA_DATA_stacked_10Nov2015.csv" ea_stacked


#echo "Loading Binford Variables"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_variable_names+categories.csv" bf_vars

#echo "Loading Binford Variable Codes"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_variable_codebook.csv" bf_codes

#echo "Loading Binford Variable Values"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_vals.csv" bf_vals

#echo "Loading Geographic regions from shapefile"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/geo/level2-shape/level2.shp" geo

#TREE_FILES="${REPO_DEST}/trees/*.trees"
#for tree_file in $TREE_FILES; do
#    echo "Loading Language tree $tree_file"   
#    if [[ $tree_file == *"glotto"* ]]
#    then
#        python "${DPLACE_PATH}/dplace_app/load.py" "$tree_file" glottotree
#    else
#        python "${DPLACE_PATH}/dplace_app/load.py" "$tree_file" tree
#    fi
#done


