#!/bin/bash

# Shell script to populate D-PLACE models with data from CSV files
# CSV files are in a private GitHub repository.
# Should be run after activating virtualenv

# Make sure that the console accepts UTF-8 (which is the default on MacOSX but NOT on any
# other UNIX systems since the debug info can contain non-ASCII characters)

export LC_ALL="en_US.UTF-8"

BASEDIR=$(dirname $0)

REPO_SRC="git@github.com:SimonGreenhill/dplace-data.git"
REPO_DEST="${BASEDIR}/datasets"
DPLACE_PATH="${BASEDIR}"

# Clone the repository
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

# Loading Societies
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/EA_Society_HeaderData.csv" \
 "${REPO_DEST}/csv/Binford_Society_HeaderData.csv" \
 soc

# Loading Geographic regions
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/geo/level2.json" geo

# Linking Societies to Locations
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/society_locations.csv" soc_lat_long

# Loading Variables
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/EAVariableList_1Mar2016.csv" \
 "${REPO_DEST}/csv/BinfordVariableList_3Mar2016_utf8.csv" \
 vars

# Loading Variable Codes
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/EACodeDescriptions_1Mar2016.csv" \
 "${REPO_DEST}/csv/BinfordCodeDescriptions_3Mar2016_utf8.csv" \
 codes

# Linking Societies to Languoids
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/xd_id_to_language.csv" \
 "${REPO_DEST}/csv/glottolog.csv" \
 xd_lang

# Loading References
python "${DPLACE_PATH}/dplace_app/load.py" \
  "${REPO_DEST}/csv/ReferenceMapping_1Mar2016.csv" \
  "${REPO_DEST}/csv/BinfordReferenceMapping_3Mar2016_utf8.csv" \
  refs

# Loading Data
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/EA_DATA_Stacked_1Mar2016.csv" \
 "${REPO_DEST}/csv/Binford_DATA_stacked_5Mar2016_utf8.csv" \
 vals

# Loading Environmental Data
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EnvironmentalVariables_3Mar2016_utf8.csv" "env_vars"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.04Mar16_utf8.csv" "env_vals"

# Loading Trees
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/trees/" tree
