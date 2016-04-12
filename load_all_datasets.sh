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
	cd $REPO_DEST && git pull origin master && cd "$orig"
fi

## import the data

export DJANGO_SETTINGS_MODULE=dplace.settings
export PYTHONPATH=$DPLACE_PATH

python "${DPLACE_PATH}/dplace_app/load.py"
