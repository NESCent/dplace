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

# Clone the repository
if [ ! -d "$REPO_DEST" ]; then
	mkdir -p "$REPO_DEST"
	git clone $REPO_SRC $REPO_DEST
else
	orig=`pwd`
	cd $REPO_DEST && git pull && cd "$orig"
	mkdir -p "$REPO_DEST"
	git clone $REPO_SRC $REPO_DEST
fi

## import the data

export DJANGO_SETTINGS_MODULE=dplace.settings
export PYTHONPATH=$DPLACE_PATH

# WILL NOT WORK PRESENTLY ----
#echo "Loading ISO Codes from Ethnologue"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" iso
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" iso

#echo "Loading Languages from Ethnologue"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed-ISO693-3-current.csv" langs
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_10_2014-17th_Ed_Missing_ISO_codes.csv" langs

echo "Loading Glottolog Languages"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/glottolog_mapping_11Dec2015.csv" glotto

echo "Mapping ISOCodes to Glottolog Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/glottolog_mapping.csv" glotto_iso

echo "Loading EA Variables"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EAVariableList_17Nov2015.csv" vars

echo "Loading EA Variable Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EACodeDescriptions_17Nov2015.csv" codes

echo "Loading Binford Variables"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/BinfordVariableList_18Nov2015.csv" vars

echo "Loading Binford Variable Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/BinfordVariableListCodeDescription_18Nov2015.csv" codes

echo "Loading EA Societies"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EA_Society_HeaderData.csv" ea_soc

echo "Loading Binford Societies"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Binford_Society_HeaderData.csv" bf_soc

echo "Linking Societies to Locations"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EA_Binford_Lat_Long.csv" soc_lat_long

echo "Linking Societies to Glottocodes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/xd_id_to_language_25Jan2016.csv" xd_lang

echo "Loading References"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ReferenceMapping_11Nov2015.csv" refs

# TODO -- check?
#echo "Loading References for EA data"
#python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EA_DATA_Stacked_17Nov2015.csv" ea_refs

echo "Loading Data"
python "${DPLACE_PATH}/dplace_app/load.py" \
 "${REPO_DEST}/csv/EA_DATA_Stacked_17Nov2015.csv" \
 "${REPO_DEST}/csv/Binford_merged_18Nov2015.csv" \
 vals

echo "Loading Environmental Data"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EcologicalData.DBASE.07Mar14.csv" "env_vals"

echo "Loading Geographic regions from shapefile"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/geo/level2-shape/level2.shp" geo

echo "Loading Trees"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/trees/" tree
