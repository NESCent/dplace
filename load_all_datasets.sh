#!/bin/bash

# Shell script to populate D-PLACE models with data from the dplace-data repository.
# The path to the local clone/export of dplace-data must be passed as argument to this
# script.
# Should be run after activating virtualenv

# Make sure that the console accepts UTF-8 (which is the default on MacOSX but NOT on any
# other UNIX systems since the debug info can contain non-ASCII characters)

export LC_ALL="en_US.UTF-8"

DPLACE_PATH=$(dirname $0)

export DJANGO_SETTINGS_MODULE=dplace.settings
export PYTHONPATH=$DPLACE_PATH

python "${DPLACE_PATH}/dplace_app/load.py" $1
