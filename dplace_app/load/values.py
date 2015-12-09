# -*- coding: utf-8 -*-
# __author__ = 'stef'

import csv
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

def load_val_references(val_row):
    if not 'soc_id' in val_row:
        return
        
    ext_id = val_row['soc_id'].strip()
    if ext_id == "":
        return

    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
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
        print "Could not determine dataset source for row %s, skipping" % str(val_row)
        return

    variable = get_variable(variable_id, label)
    value = val_row['Code'].strip()
    comment = val_row['Comment'].strip()
    references = val_row['References'].strip().split(";")   
    focal_year = val_row['Year'].strip()

    if variable is None:
        print "Could not find variable %s for society %s" % (variable_id, society)
        return

    code = get_description(variable, value)
    
    try:
        v = VariableCodedValue.objects.get(
            variable=variable, 
            society=society, 
            source=source, 
            coded_value=value,
            code=code,
            focal_year=focal_year,
            comment=comment,
        )
        
    except:
        print "Could not find VariableCodedValue for Society %s Variable %s, skipping" % (society, variable.label)
        return
        
    for r in references:
        ref_short = r.split(",")
        if len(ref_short) == 2:
            author = ref_short[0].strip()
            year = ref_short[1].strip()
            try:
                ref = Source.objects.get(author=author, year=year)
                if ref not in v.references.all():
                    v.references.add(ref)
            except ObjectDoesNotExist:
                print "Could not find reference %s (%s) in database, skipping reference" % (author, year)

    v.save()
    print "Saved references for Society %s Variable %s" % (ext_id, variable.label)
        
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
        print "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
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
        print "Could not determine dataset source for row %s, skipping" % str(val_row)
        return

    variable = get_variable(variable_id, label)
    value = val_row['Code'].strip()
    comment = val_row['Comment'].strip()
    references = val_row['References'].strip().split(";")   
    focal_year = val_row['Year'].strip()
    subcase = val_row['SpecRef'].strip()

    if variable is None:
        print "Could not find variable %s for society %s" % (variable_id, society)
        return

    code = get_description(variable, value)
    
    v, created = VariableCodedValue.objects.get_or_create(
        variable=variable,
        society=society,
        source=source,
        coded_value=value,
        code=code,
        focal_year=focal_year,
        comment=comment,
        subcase=subcase
    )
    v.save()
    print "Saved data for Society %s Variable ID %s" % (ext_id, variable.label)

