# -*- coding: utf-8 -*-
import csv
import logging
from dplace_app.models import *

from sources import get_source
from util import eavar_number_to_label, bfvar_number_to_label


DATASET_COLUMN              = 0
ID_COLUMN                   = 1
CODE_COLUMN                 = 2
DESCRIPTION_COLUMN          = 4   
SHORT_DESCRIPTION_COLUMN    = 5


def clean_category(category):
    return category.strip().capitalize()


def load_vars(var_dict):
    """
    Load variables from VariableList.csv
    """
    if var_dict['Dataset'] == 'EA':
        label = eavar_number_to_label(var_dict['VarID'])
        source = get_source("EA")
    elif var_dict['Dataset'] == 'LRB':
        label = bfvar_number_to_label(var_dict['VarID'])
        source = get_source("Binford")
    else:
        logging.warn("Dataset %(Dataset)s not in database, skipping row" % var_dict)
        return

    variable, created = CulturalVariable.objects.get_or_create(
        label=label, source=source)
    variable.name = var_dict['VarTitle']
    variable.codebook_info = var_dict['VarDefinition']
    variable.data_type = var_dict['VarType']
    for c in map(clean_category, var_dict['IndexCategory'].split(',')):
        index_category, created = CulturalCategory.objects.get_or_create(name=c)
        logging.info("Created CulturalCategory: %s" % c)
        if index_category not in variable.index_categories.all():
            variable.index_categories.add(index_category)
    variable.save()
    logging.info("Created CulturalVariable: %s" % label)
    logging.info("Saved variable %s - %s" % (label, variable.name))


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

        variable = CulturalVariable.objects.get(label=label)
        if variable:
            code_description, created = CulturalCodeDescription.objects.get_or_create(variable=variable, code=code)
            code_description.description = description
            code_description.short_description = short_description
            code_description.save()
            logging.info("Created CulturalCodeDescription: %s" % code_description)
        else:
            logging.warn("Missing variable in database: %s" % label)
