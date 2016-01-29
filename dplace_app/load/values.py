# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *
from sources import get_source
from util import eavar_number_to_label, bfvar_number_to_label


_VAL_CACHE, _VCD_CACHE = {}, {}


def get_variable(label):
    if label not in _VAL_CACHE:
        try:
            _VAL_CACHE[label] = VariableDescription.objects.get(label=label)
        except ObjectDoesNotExist:
            _VAL_CACHE[label] = None
    return _VAL_CACHE[label]


def get_description(variable, value):
    key = (variable, value)
    if key not in _VCD_CACHE:
        try:
            # Check for Code description if it exists.
            _VCD_CACHE[key] = VariableCodeDescription.objects.get(variable=variable,code=value)
        except ObjectDoesNotExist:
            _VCD_CACHE[key] = None
    return _VCD_CACHE[key]


#soooooooooooooooooooooooooo slow 
def load_data(val_row):
    ext_id = val_row.get('soc_id')
    if not ext_id:
        return

    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        logging.warn(
            "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
        )
        return

    variable_id = val_row['VarID']

    if val_row['Dataset'] == 'EA':
        source = get_source("EA")
        label = eavar_number_to_label(variable_id)
    elif val_row['Dataset'] == 'LRB':
        source = get_source("Binford")
        label = bfvar_number_to_label(variable_id)
    else:
        logging.warn("Could not determine dataset source for row %s, skipping" % str(val_row))
        return

    variable = get_variable(label)
    if variable is None:
        logging.warn("Could not find variable %s for society %s" % (variable_id, society.name))
        return

    code = get_description(variable, val_row['Code'].strip())
    
    v, created = VariableCodedValue.objects.get_or_create(
        variable=variable,
        society=society,
        source=source,
        coded_value=val_row['Code'],
        code=code,
        focal_year=val_row['Year'],
        comment=val_row['Comment'],
        subcase=val_row['SpecRef'])
    
    if created:
        logging.info("Saved data for Society %s Variable ID %s" % (ext_id, variable.label))

    for r in val_row['References'].split(";"):
        ref_short = r.split(",")
        if len(ref_short) == 2:
            author = ref_short[0].strip()
            year = ref_short[1].strip()
            try:
                ref = Source.objects.get(author=author, year=year)
                if ref not in v.references.all():
                    v.references.add(ref)
                    logging.info("Adding reference %s (%s) to %s" % (author, year, v))
            except ObjectDoesNotExist:
                logging.warn(
                    "Could not find reference %s (%s) in database, skipping reference"
                    % (author, year))
    return v
