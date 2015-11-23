# -*- coding: utf-8 -*-
# __author__ = 'stef'

import csv
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.models import *
from sources import get_source

def ea_soc_to_xd_id(dict_row):
    soc_id = dict_row['soc_id']
    xd_id = dict_row['xd_id']
    try:
        society = Society.objects.get(ext_id=soc_id)
        society.xd_id = xd_id
        society.save()
    except ObjectDoesNotExist:
        "Warning: Unable to find society %s" % soc_id
        return

def load_ea_society(society_dict):
    ext_id = society_dict['soc_id'].strip()
    xd_id = society_dict['xd_id'].strip()
    soc_name = society_dict['soc_name'].strip()
    source = get_source('EA')
    focal_year = society_dict['main_focal_year'].strip()
    alternate_names = society_dict['alternate_names'].strip()
    
    society, created = Society.objects.get_or_create(ext_id=ext_id)
    society.xd_id = xd_id
    society.source = source
    society.name = soc_name
    society.alternate_names = alternate_names
    society.focal_year = focal_year
    
    print "Saving society %s" % society
    society.save()
    
def society_locations(dict_row):
    '''
    Locations for societies from EA_Binford_Lat_Long.csv.
    '''
    soc_id = dict_row['soc_id']
    lat_val = dict_row['Latitude']
    long_val = dict_row['Longitude']
    
    try:
        society = Society.objects.get(ext_id=soc_id)
        try:
            location = Point(
                float(long_val),
                float(lat_val)
            )
            society.location = location
        except ValueError:
            print "Unable to create Point from (%s,%s) for society %s" % (long_val, lat_val, society)
        society.save()
    except ObjectDoesNotExist:
        print "No society with ID %s in database, skipping" % soc_id

def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)

_EA_VAL_CACHE, _EA_VCD_CACHE = {}, {}
def get_variable(number):
        label = eavar_number_to_label(number)
        if label not in _EA_VAL_CACHE:
            try:
                _EA_VAL_CACHE[label] = VariableDescription.objects.get(label=label)
            except ObjectDoesNotExist:
                _EA_VAL_CACHE[label] = None
        return _EA_VAL_CACHE[label]
    
def get_description(variable, value):
    key = (variable, value)
    if key not in _EA_VCD_CACHE:
        try:
            # Check for Code description if it exists.
            _EA_VCD_CACHE[key] = VariableCodeDescription.objects.get(variable=variable,code=value)
        except ObjectDoesNotExist:
            _EA_VCD_CACHE[key] = None
    return _EA_VCD_CACHE[key]

def load_ea_references(val_row):

    ext_id = val_row['soc_id'].strip()
    
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA references for %s but did not find an existing Society object, skipping" % ext_id
        return
        
    source = get_source("EA")
    variable = get_variable(val_row['VarID'].strip())
    value = val_row['Code'].strip()
    focal_year = val_row['Year'].strip()
    references = val_row['References'].strip().split(";")
    
    if variable is None:
        print "Could not find variable %s for society %s" % (val_row['VarID'], society)
        return

    code = get_description(variable, value)
    
    try:
        v = VariableCodedValue.objects.get(
            variable=variable, 
            society=society, 
            source=source, 
            coded_value=value,
            code=code,
            focal_year=focal_year
        )
            
        if len(references) == len(v.references.all()):
            print "References already saved for Society %s Variable %s, skipping" % (society, variable.label)
            return
    except:
        print "Could not find VariableCodedValue for Society %s Variable %s, skipping" % (society, variable.label)
        return
    refs = []
    for r in references:
        ref_short = r.split(",")
        if len(ref_short) == 2:
            author = ref_short[0].strip()
            year = ref_short[1].strip()
            try:
                ref = Source.objects.get(author=author, year=year)
                refs.append(ref)
            except ObjectDoesNotExist:
                print "Could not find reference %s (%s) in database, skipping reference" % (author, year)
    v.references.add(*refs)
    v.save()
    print "Saved references for Society %s Variable %s" % (ext_id, variable.label)
        
        
#soooooooooooooooooooooooooo slow 
def load_ea_stacked(val_row):
    if not 'soc_id' in val_row and not 'ID' in val_row:
        return
    if 'soc_id' in val_row:
        ext_id = val_row['soc_id'].strip()
    else:
        ext_id = val_row['ID'].strip()
    source = get_source("EA")
    # find the existing society
    
    if ext_id == "":
        assert all([val_row[cell] == "" for cell in val_row])
        return
        
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
        return
            
    variable = get_variable(val_row['VarID'].strip())
    value = val_row['Code'].strip()
    comment = val_row['Comment'].strip()
    references = val_row['References'].strip().split(";")   
    focal_year = val_row['Year'].strip()

    if variable is None:
        print "Could not find variable %s for society %s" % (val_row['VarID'], society)
        return

    code = get_description(variable, value)
    
    v, created = VariableCodedValue.objects.get_or_create(
        variable=variable,
        society=society,
        source=source,
    )
    v.coded_value = value
    v.code = code
    v.comment = comment
    v.focal_year = focal_year

    #for r in references:
     #   ref_short = r.split(",")
     #   if len(ref_short) == 2:
     #       author = ref_short[0].strip()
     #       year = ref_short[1].strip()
     #       try:
     #           ref = Source.objects.get(author=author, year=year)
     #           if ref not in v.references.all():
     #               v.references.add(ref)
     #       except ObjectDoesNotExist:
     #           print "Could not find reference %s (%s) in database, skipping reference for this coded value %s" % (author, year, v)
    v.save()
    print "Saved data for Society %s Variable ID %s" % (ext_id, variable.label)


