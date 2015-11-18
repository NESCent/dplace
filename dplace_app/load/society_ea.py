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
        
#----------------------------------NEW CODE FOR GETTING EA CODE DESCRIPTIONS, NOV 7 2015--------------------------------------------#
DATASET_COLUMN          = 0
ID_COLUMN               = 1
CODE_COLUMN             = 2
DESCRIPTION_COLUMN      = 4   
def load_codes(csvfile=None):
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        dataset = row[DATASET_COLUMN].strip()
        if dataset=='Dataset': #skip header
            continue
        code = row[CODE_COLUMN].strip()
        id = row[ID_COLUMN].strip()
        description = row[DESCRIPTION_COLUMN].strip()
        if dataset=='EA':
            ea_label = eavar_number_to_label(id)
            variable = VariableDescription.objects.get(label=ea_label)
            if variable:
                code_description, created = VariableCodeDescription.objects.get_or_create(variable=variable, code=code)
                description = description.decode("windows-1252").replace(u"\u2019", "'") #replace Windows smart apostrophe
                code_description.description = description
                code_description.save()
            else:
                "Missing variable in database: %s" % ea_label

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
            print "load_ea_codes: did not get anything from %s row %s " % (csvfile.name, ','.join(row)[0:30])




_EA_VAL_CACHE, _EA_VCD_CACHE = {}, {}
#soooooooooooooooooooooooooo slow 
#need to read in references
def load_ea_stacked(val_row):
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
    
    variable = get_variable(val_row['VarID'])
    value = val_row['Code']
    comment = val_row['Comment']
    references = val_row['References'].strip().split(";")

    if variable is None:
        print "Could not find variable %s for society %s" % (val_row['VarID'], society)
        return

    code = get_description(variable, value)
    
    v, created = VariableCodedValue.objects.get_or_create(
        variable=variable,
        society=society,
        source=source,
        coded_value=value,
        code=code,
    )
    for r in references:
        ref_short = r.split(",")
        if len(ref_short) == 2:
            author = ref_short[0].strip()
            year = ref_short[1].strip()
            try:
                ref = Source.objects.get(author=author, year=year)
                if ref not in v.references.all():
                    print "Adding reference %s" % (ref)
                    v.references.add(ref)
            except ObjectDoesNotExist:
                print "Could not find reference %s (%s) in database, skipping reference for this coded value %s" % (author, year, v)

    if created:
        print "Getting data for Society %s Variable ID %s" % (ext_id, val_row['VarID'])
    v.save()

