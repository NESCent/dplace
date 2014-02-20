#!/bin/bash

# Shell script to populate D-PLACE models with data from CSV files
# CSV files are in a private Bitbucket repository under the NESCent organization

BASEDIR=$(dirname $0)

REPO_SRC="git@bitbucket.org:nescent/dplace-datasets.git"
REPO_DEST="${BASEDIR}/datasets"

# Path to your virtualenv, you will likely need to change this
ENV_PATH="${BASEDIR}/../env-dplace"
DPLACE_PATH="${BASEDIR}"

if [ ! -d "$ENV_PATH" ]; then
  echo "ERROR: Virtualenv at '$ENV_PATH' not found"
  echo "Please edit $0 and set the path to your Python Virtualenv"
  exit -1
fi

## Clone the repository
if [ ! -d "$REPO_DEST" ]; then
	mkdir -p "$REPO_DEST"
	git clone $REPO_SRC $REPO_DEST
else
  orig=`pwd`
  cd $REPO_DEST && git pull && cd "$orig"
fi

## Activate the virtualenv
source "${ENV_PATH}/bin/activate"

## import the data

export DJANGO_SETTINGS_MODULE=dplace.settings
export PYTHONPATH=$DPLACE_PATH

echo "Loading ISO Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/iso_lat_long.csv" iso
echo "Loading EA Societies"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Lat_Long_data_EA_Binford_Societies_Oct8_2013-3.csv" soc
echo "Loading Environmental Data"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/EnvironmentalDataset.15Oct2013.csv" "env"
echo "Loading EA Variables"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_variable_names.csv" ea_vars
echo "Loading EA Variable Codes"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_codes.csv" ea_codes
echo "Loading EA Variable Values"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/ea_vals.csv" ea_vals
echo "Loading Languages"
python "${DPLACE_PATH}/dplace_app/load.py" "${REPO_DEST}/csv/Revised_Ethnologue_families-Feb_6_2014-17th_Ed-ISO693-3-current.csv"  langs
