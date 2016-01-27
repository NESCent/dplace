# -*- coding: utf-8 -*-
# __author__ = 'Stef'
# used to load variables

import csv
import logging
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.models import *
from sources import get_source

DATASET_COLUMN              = 0
ID_COLUMN                   = 1
CODE_COLUMN                 = 2
DESCRIPTION_COLUMN          = 4   
SHORT_DESCRIPTION_COLUMN    = 5


def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)
    
def bfvar_number_to_label(number):
    return "B{0:0>3}".format(number)
    
def clean_category(category):
    return category.strip().capitalize()

def load_vars(var_dict):
    """
    Load variables from VariableList.csv
    """

    dataset = var_dict['Dataset'].strip()
    index_categories = [clean_category(x) for x in var_dict['IndexCategory'].split(',')]
    id = var_dict['VarID']
    name = var_dict['VarTitle']
    description = var_dict['VarDefinition']
    datatype = var_dict['VarType']
    
    if dataset=='EA':
        label = eavar_number_to_label(id)
        source = get_source("EA")
    elif dataset=='LRB':
        label = bfvar_number_to_label(id)
        source = get_source("Binford")
    else:
        logging.warn("Dataset %s not in database, skipping row" % (dataset, str(var_dict)))
        return
    variable, created = VariableDescription.objects.get_or_create(label=label, source=source)
    variable.name = name
    variable.codebook_info = description
    variable.data_type = datatype
    for c in index_categories:
        index_category, created = VariableCategory.objects.get_or_create(name=c)
        logging.info("Created VariableCategory: %s" % c)
        if index_category not in variable.index_categories.all():
            variable.index_categories.add(index_category)
    variable.save()
    logging.info("Created VariableDescription: %s" % label)
    logging.info("Saved variable %s - %s" % (label, name))
    
def load_codes(csvfile=None):
    '''
    Used to load Code Descriptions from CodeDescriptions.csv.
    '''
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        dataset = row[DATASET_COLUMN].strip()
        if dataset=='Dataset': #skip header
            continue
        code = row[CODE_COLUMN].strip()
        id = row[ID_COLUMN].strip()
        description = row[DESCRIPTION_COLUMN].strip()
        short_description = row [SHORT_DESCRIPTION_COLUMN].strip()
        
        if dataset=='EA':
            label = eavar_number_to_label(id)
        elif dataset=='LRB':
            label = bfvar_number_to_label(id)
        else:
            logging.warn("No dataset %s in database, skipping row %s" % (dataset, str(row)))
            continue

        variable = VariableDescription.objects.get(label=label)
        if variable:
            code_description, created = VariableCodeDescription.objects.get_or_create(variable=variable, code=code)
            code_description.description = description
            code_description.short_description = short_description
            code_description.save()
            logging.info("Created VariableCodeDescription: %s" % code_description)
        else:
            logging.warn("Missing variable in database: %s" % label)

        
