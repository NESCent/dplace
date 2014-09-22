#!/bin/bash

# Shell script to populate D-PLACE models with data from CSV files
# CSV files are in a private Bitbucket repository under the NESCent organization
# Should be run after activating virtualenv

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

echo "Loading ISO Codes from Ethnologue"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" iso
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" iso

echo "Loading ISO Code Lat/Long"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/iso_lat_long.csv" iso_lat_long

echo "Loading Languages from Ethnologue"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" langs
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" langs

echo "Loading EA Societies"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_langs+isocodes.csv" ea_soc

echo "Loading Binford Societies"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_langs+isocodes.csv" bf_soc

echo "Loading Environmental Data"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.07Mar14.csv" "env_vars"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.07Mar14.csv" "env_vals"

echo "Loading EA Variables"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_variable_names+categories.csv" ea_vars
echo "Loading EA Variable Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_codes.csv" ea_codes
echo "Loading EA Variable Values"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_vals.csv" ea_vals

echo "Loading Binford Variables"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_variable_names+categories.csv" bf_vars

echo "Loading Binford Variable Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_variable_codebook.csv" bf_codes

echo "Loading Binford Variable Values"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/binford_vals.csv" bf_vals

echo "Loading Geographic regions from shapefile"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/geo/level2-shape/level2.shp" geo

TREE_FILES="${REPO_DEST}/trees/*.trees"
for tree_file in $TREE_FILES; do
    echo "Loading Language tree $tree_file"
    python "${DPLACE_PATH}/dplace_app/load.py" "$tree_file" tree
done
