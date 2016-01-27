# -*- coding: utf-8 -*-
# __author__ = 'stef'

import csv
import logging
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.models import *
from sources import get_source

def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)
    
def bfvar_number_to_label(number):
    return "B{0:0>3}".format(number)

_VAL_CACHE, _VCD_CACHE = {}, {}
def get_variable(number, label):
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
    if not 'soc_id' in val_row:
        return
        
    ext_id = val_row['soc_id'].strip()
    if ext_id == "":
        return

    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        logging.warn(
            "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
        )
        return
        
    variable_id = val_row['VarID'].strip()

    if val_row['Dataset'].strip() == 'EA':
        source = get_source("EA")
        label = eavar_number_to_label(variable_id)
        
    elif val_row['Dataset'].strip() == 'LRB':
        source = get_source("Binford")
        label = bfvar_number_to_label(variable_id)
        
    else:
        source = None
        logging.warn("Could not determine dataset source for row %s, skipping" % str(val_row))
        return
    
    variable = get_variable(variable_id, label)
    
    if variable is None:
        logging.warn("Could not find variable %s for society %s" % (variable_id, society))
        return
        
    code = get_description(variable, val_row['Code'].strip())
    
    v, created = VariableCodedValue.objects.get_or_create(
        variable=variable,
        society=society,
        source=source,
        coded_value=val_row['Code'].strip(),
        code=code,
        focal_year=val_row['Year'].strip(),
        comment=val_row['Comment'].strip(),
        subcase=val_row['SpecRef'].strip()
    )
    
    if created:
        logging.info("Saved data for Society %s Variable ID %s" % (ext_id, variable.label))
        
    references = val_row['References'].strip().split(";")
    for r in references:
        ref_short = r.split(",")
        if len(ref_short) == 2:
            author = ref_short[0].strip()
            year = ref_short[1].strip()
            try:
                ref = Source.objects.get(author=author, year=year)
                if ref not in v.references.all():
                    v.references.add(ref)
                    logging.info(
                        "Adding reference %s (%s) to %s" % (author, year, v)
                    )
            except ObjectDoesNotExist:
                logging.warn(
                    "Could not find reference %s (%s) in database, skipping reference" % (author, year)
                )
    
    