# -*- coding: utf-8 -*-
# __author__ = 'dan'

import csv
import re
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError, DataError
from dplace_app.load.isocode import get_isocode
from dplace_app.models import *
from environmental import iso_from_code
from society_ea import clean_category
from sources import get_source

def load_bf_harm(society_dict):
    ext_id = society_dict['Binford_ID']
    found_societies = Society.objects.filter(ext_id=ext_id)
    if len(found_societies) > 0:
        society = found_societies.first()
        society.focal_year = society_dict['Binford_FocalYear']
        society.references = society_dict['Binford_references']
        try:
            society.save()
        except BaseException as e:
            print "Exception saving society: %s" % e.message
            return None
        return society
    return found_societies.first()

def _unicode_damnit(var):
    return var.decode('latin1').encode('utf8')


def load_bf_society(society_dict):
    ext_id = society_dict['ID']
    source = get_source("Binford")
    found_societies = Society.objects.filter(ext_id=ext_id, source=source)
    if len(found_societies) == 0:
        iso_code = iso_from_code(get_isocode(society_dict))
        
        if iso_code is None:
            print "Warning: Unable to find a record for ISO code %s" % get_isocode(society_dict)
        
        # Get the language
        language_name = society_dict['LangNam']
        try:
            language = Language.objects.get(name=language_name, iso_code=iso_code)
        except ObjectDoesNotExist:
            language = None
            print "Warning: Creating society record for %s but no language found with name %s" % (ext_id, language_name)
        
        society = Society(
            ext_id=ext_id,
            name=society_dict['STANDARD SOCIETY NAME Binford'],
            source=source,
            iso_code=iso_code,
            language=language
        )
        
        try:
            society.save()
        except BaseException as e:
            print "Exception saving society: %s" % e.message
            return None
        return society
    else:
        society = found_societies.first()
        if not society.source:
            society.source = source
        try:
            society.save()
        except BaseException as e:
            print "Exception saving society: %s" % e.message
            return None
        return society
    return found_societies.first()

def load_bf_var(var_dict):
    """
    Variables are loaded form binford_variable_names+categories.csv for simplicity,
    but there is more detailed information in bf_codebook.csv
    """
    label = var_dict['Field Name'].strip()
    name = var_dict['Variable name'].strip()
    description = var_dict['Detailed description'].strip()
    data_type = var_dict['DataType'].strip()
    
    found_variables = VariableDescription.objects.filter(label=label)
    if len(found_variables) == 0: #creating a new variable isn't working at the moment
        print name
        return None
    else:
        variable = found_variables.first()
        print variable
        variable.data_type = data_type
        try:
            variable.save()
        except BaseException as e:
            print e
    
    index_categories = [clean_category(x) for x in var_dict['IndexCategory'].split(',')]
    # Currently max 1 niche category
    niche_categories = [clean_category(x) for x in var_dict['NicheCategory'].split(',')]

    # when creating categories, ignore '?'
    for category_name in index_categories:
        index_category, created = VariableCategory.objects.get_or_create(name=category_name)
        var.index_categories.add(index_category)
    for category_name in niche_categories:
        niche_category, created = VariableCategory.objects.get_or_create(name=category_name)
        var.niche_categories.add(niche_category)
    return

VARIABLE_DEF_EXPRESSION = 'B[0-9]{3}_.*'
BF_CODE_COLUMN_VARIABLE_DEF = 0
BF_CODE_COLUMN_VARIABLE_NAME = 6
BF_CODE_COLUMN_VARIABLE_DESC = 8

def read_binford_variable_def(csv_reader):
    '''
    Advances the CSV reader row-by-row until finding a row that starts with
    VARIABLE_DEF_EXPRESSION
    '''
    row, matched = None, None
    while matched is None:
        try:
            row = csv_reader.next()
        except StopIteration:
            return None
        matched = re.match(VARIABLE_DEF_EXPRESSION, row[BF_CODE_COLUMN_VARIABLE_DEF])
    variable_def = dict()
    variable_def['field'] = row[BF_CODE_COLUMN_VARIABLE_DEF]
    variable_def['name'] = row[BF_CODE_COLUMN_VARIABLE_NAME]
    variable_def['desc'] = row[BF_CODE_COLUMN_VARIABLE_DESC]
    return variable_def

def read_binford_header_row(csv_reader):
    '''
    Advances the CSV reader row-by-row until finding a row with CODE,DESCRIPTION,NOTES
    '''
    row, matched = None, False
    while not matched:
        try:
            row = csv_reader.next()
        except StopIteration:
            return None
        matched = row[0].strip() == 'CODE'
    return row

def read_binford_code_rows(csv_reader):
    '''
    Advances the CSV reader row-by-row, collecting CODE / DESCRIPTION / NOTES / PAGE rows
    until a blank row is found
    '''
    codes, done = [], False
    while not done:
        try:
            row = csv_reader.next()
        except StopIteration:
            done = True
            break
        if len(row[0].strip()) == 0:
            done = True
        else:
            codes.append({'code': row[0].strip(),
                         'description': row[1].strip(),
                         'notes': row[2].strip(),
                         'page': row[3].strip()
            })
    return codes


def load_bf_codes(csvfile=None):
    csv_reader = csv.reader(csvfile)
    # parse the file, looking for variable def, then header, then codes
    variable_def = read_binford_variable_def(csv_reader)
    while variable_def is not None:
        read_binford_header_row(csv_reader)
        codes = read_binford_code_rows(csv_reader)
        label = _unicode_damnit(variable_def['field'])
        variable = VariableDescription.objects.get(label=label)
        for code in codes:
            # Special cases
            if code['code'].startswith('class:'):
                print "Code %s starts with 'class:', skipping" % code['code']
                continue
            if code['code'].startswith('Value'):
                print "Code %s starts with 'Value', skipping" % code['code']
                continue
            code_description = VariableCodeDescription.objects.get_or_create(
                variable=variable,
                code=code['code'],
                description=_unicode_damnit(code['description'])
            )
        
        # Set up for next pass
        variable_def = read_binford_variable_def(csv_reader)


def load_bf_val(val_row):
    ext_id = val_row['ID'].strip()
    source = get_source("Binford")
    # find the existing society
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load Binford values for %s but did not find an existing Society object" % ext_id
        return
    # Variable values are in columns after 'ID' and 'Name'
    for key in val_row.keys():
        if key not in ('ID', 'Name'):
            label = key
            value = val_row[key].strip()
            try:
                variable = VariableDescription.objects.get(label=label)
            except ObjectDoesNotExist:
                continue
            try:
                # Check for Code description if it exists.
                code = VariableCodeDescription.objects.get(variable=variable,code=value)
            except ObjectDoesNotExist:
                code = None
            try:
                variable_value = VariableCodedValue(variable=variable,
                                                    society=society,
                                                    coded_value=value,
                                                    code=code)
                variable_value.save()
            except IntegrityError:
                print "Unable to store value '%s' for var %s in society %s, already exists" % (value, variable.label, society)
            except DataError:
                print "data error saving '%s'" % value


def postprocess_binford_societies():
    '''
    Some of the EA Variable values represent data that is needed at the society level, e.g.
    source and location
    '''
    try:
        lon_var = VariableDescription.objects.get(label='revised.longitude')
        lat_var = VariableDescription.objects.get(label='revised.latitude')
    except ObjectDoesNotExist:
        print "Unable to find vars for Lon/Lat.  Have you loaded the bf_vars?"
    for society in Society.objects.filter(source=get_source("Binford")):
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
            # TODO: Get source, incl focal year
        society.save()
