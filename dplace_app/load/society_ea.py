# -*- coding: utf-8 -*-
# __author__ = 'dan'

import csv
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.load.isocode import get_isocode
from dplace_app.models import *
from environmental import iso_from_code
from sources import get_source
# TODO: figure out how to deal with focal year.

def load_ea_society(society_dict):
    ext_id = society_dict['ID']
    source = get_source('EA')
    found_societies = Society.objects.filter(ext_id=ext_id, source=get_source("EA"))
    if len(found_societies) == 0:
        name = society_dict['Society_name_EA']
        iso_code = iso_from_code(get_isocode(society_dict))
        if iso_code is None:
            print "Warning: Unable to find a record for ISO code %s" % get_isocode(society_dict)
        # Get the language
        language_name = society_dict['LangNam']
        try:
            language = Language.objects.get(name=language_name,iso_code=iso_code)
        except ObjectDoesNotExist:
            language = None
            print "Warning: Creating society record for %s but no language found with name %s" % (ext_id, language_name)
        society = Society(ext_id=ext_id,
                          name=name,
                          source=source,
                          iso_code=iso_code,
                          language=language
                          )
        try:
            society.save()
            return society
        except BaseException as e:
            print "Exception saving society: %s" % e.message
            return None
    else:
        return found_societies.first()

def postprocess_ea_societies():
    '''
    Some of the EA Variable values represent data that is needed at the society level, e.g.
    source and location
    '''
    try:
        lon_var = VariableDescription.objects.get(name='Longitude')
        lat_var = VariableDescription.objects.get(name='Latitude')
        focal_year_var = VariableDescription.objects.get(name='Date: Year with Century')
    except ObjectDoesNotExist:
        print "Unable to find vars for Lon/Lat/Year.  Have you loaded the ea_vars?"
    for society in Society.objects.filter(source=get_source("EA")):
        # Get location
        try:
            lon_val = society.variablecodedvalue_set.get(variable=lon_var)
            lat_val = society.variablecodedvalue_set.get(variable=lat_var)
        except ObjectDoesNotExist:
            print "Unable to get lon/lat for society %s, skipping postprocessing" % society
            continue
        try:
            location = Point(
                float(lon_val.coded_value),
                float(lat_val.coded_value)
            )
            society.location = location
        except ValueError:
            print "Unable to create Point from (%s,%s) for society %s" % (lon_val.coded_value, lat_val.coded_value, society)
        society.save()

def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)

def load_ea_var(var_dict):
    """
    Variables are loaded form ea_variable_names+categories.csv for simplicity,
    but there is more detailed information in ea_codes.csv
    """
    try:
        number = int(var_dict['Variable number'])
    except ValueError:
        return
    exclude = var_dict['Exclude from D-PLACE?']
    if exclude == '1':
        return

    label = eavar_number_to_label(number)
    name = var_dict['Variable'].strip()
    variable, created = VariableDescription.objects.get_or_create(label=label,name=name,source=get_source("EA"))

    index_categories = [clean_category(x) for x in var_dict['INDEXCATEGORY'].split(',')]
    # Currently max 1 niche category
    niche_categories = [clean_category(x) for x in var_dict['NICHECATEGORY'].split(',')]

    # when creating categories, ignore '?'
    for category_name in index_categories:
        index_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.index_categories.add(index_category)
    for category_name in niche_categories:
        niche_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.niche_categories.add(niche_category)

def clean_category(category):
    return category.strip().capitalize()

SORT_COLUMN             = 0
VARIABLE_VNUMBER_COLUMN = 1
VARIABLE_NUMBER_COLUMN  = 2
VARIABLE_NAME_COLUMN    = 3
N_COLUMN                = 4
CODE_COLUMN             = 5
DESCRIPTION_COLUMN      = 6

# e.g. N	CODE	DESCRIPTION
def row_is_headers(row):
    possible_code = row[CODE_COLUMN].strip()
    possible_n = row[N_COLUMN].strip()
    possible_desc = row[DESCRIPTION_COLUMN].strip()
    if possible_code == 'CODE' and possible_n == 'N' and possible_desc == 'DESCRIPTION':
        return True
    else:
        return False

# e.g. 1	1	Gathering 	1267
def row_is_def(row):
    possible_number = row[VARIABLE_NUMBER_COLUMN].strip()
    if possible_number.isdigit():
        return True
    else:
        return False

# has a code value and a description text
# e.g. 706	0	0 - 5% Dependence
def row_is_data(row):
    # N_row is numeric
    n_cell = row[N_COLUMN].strip()
    # variable_number is empty
    number_cell = row[VARIABLE_NUMBER_COLUMN].strip()
    # Code may be ., 0, or abc... so it's not a simple identifier
    if n_cell.isdigit() and len(number_cell) == 0:
        return True
    else:
        return False

# Junk rows
def row_is_skip(row):
    sort_cell = row[SORT_COLUMN].strip()
    if sort_cell.isdigit():
        return False
    else:
        return True

def load_ea_codes(csvfile=None):
    number = None
    variable = None
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row_is_skip(row):
            pass
        elif row_is_data(row):
            if variable is None:
                # Variable may have been excluded from D-PLACE, ignore this data row
                continue
            code = row[CODE_COLUMN].strip()
            n = row[N_COLUMN].strip()
            try:
                n = int(n)
            except ValueError:
                n = 0
            found_descriptions = VariableCodeDescription.objects.filter(variable=variable,code=code)
            if len(found_descriptions) == 0:
                # This won't help for things that specify a range or include the word or
                description = row[DESCRIPTION_COLUMN].strip()
                code_description = VariableCodeDescription(variable=variable,
                                                             code=code,
                                                             description=description,
                                                             n=n)
                code_description.save()
        elif row_is_headers(row):
            pass
        elif row_is_def(row):
            # get the variable number
            number = int(row[VARIABLE_NUMBER_COLUMN])
            try:
                # Some variables in the EA have been excluded from D-PLACE, so there
                # will be no VariableDescription object for them
                label = eavar_number_to_label(number)
                variable = VariableDescription.objects.get(label=label)
            except ObjectDoesNotExist:
                variable = None
        else:
            print "did not get anything from this row %s" % (','.join(row)).strip()




_EA_VAL_CACHE, _EA_VCD_CACHE = {}, {}
def load_ea_val(val_row):
    # So sloooow.
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
        
    ext_id = val_row['ID'].strip()
    source = get_source("EA")
    # find the existing society
    
    if ext_id == "":
        assert all([val_row[cell] == "" for cell in val_row])
        return
        
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA values for %s but did not find an existing Society object" % ext_id
        return
   
    # get the keys that start with v
    for key in val_row.keys():
        if key.find('v') == 0:
            number = int(key[1:])
            value = val_row[key].strip()
            variable = get_variable(number)
            
            if variable is None:
                continue
            
            code = get_description(variable, value)
            
            try:
                variable_value = VariableCodedValue(variable=variable,
                                                    society=society,
                                                    coded_value=value,
                                                    source=source,
                                                    code=code)
                variable_value.save()
            except IntegrityError:
                print "Unable to store value '%s' for var %s in society %s, already exists" % (value, variable.label, society)
