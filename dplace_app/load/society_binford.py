# -*- coding: utf-8 -*-
# __author__ = 'dan'

import csv
import re
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *
from environmental import iso_from_code
from society_ea import clean_category

def load_bf_society(society_dict):
    ext_id = society_dict['ID']
    source = 'Binford'
    found_societies = Society.objects.filter(ext_id=ext_id,source=source)
    if len(found_societies) == 0:
        name = society_dict['STANDARD SOCIETY NAME Binford']
        iso_code = iso_from_code(society_dict['ISO693_3'])
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
        society.save()

def load_bf_var(var_dict):
    """
    Variables are loaded form binford_variable_names+categories.csv for simplicity,
    but there is more detailed information in bf_codebook.csv
    """
    label = var_dict['Field name'].strip()
    name = var_dict['Variable name'].strip()
    description = var_dict['Detailed description'].strip()

    variable, created = VariableDescription.objects.get_or_create(label=label,name=name)

    index_categories = [clean_category(x) for x in var_dict['IndexCategory'].split(',')]
    # Currently max 1 niche category
    niche_categories = [clean_category(x) for x in var_dict['NicheCategory'].split(',')]

    # when creating categories, ignore '?'
    for category_name in index_categories:
        index_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.index_categories.add(index_category)
    for category_name in niche_categories:
        niche_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.niche_categories.add(niche_category)

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
        variable = VariableDescription.objects.get(label=variable_def['field'])
        for code in codes:
            # Special cases
            if code['code'].startswith('class:'):
                print "Code %s starts with 'class:', skipping" % code['code']
                continue
            if code['code'].startswith('Value'):
                print "Code %s starts with 'Value', skipping" %code['code']
            code_description = VariableCodeDescription.objects.get_or_create(variable=variable,
                                                                             code=code['code'],
                                                                             description=code['description'])
        # Set up for next pass
        variable_def = read_binford_variable_def(csv_reader)
