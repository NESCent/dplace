# -*- coding: utf-8 -*-
import logging
from dplace_app.models import CulturalVariable, CulturalCategory, CulturalCodeDescription

from sources import get_source
from util import eavar_number_to_label, bfvar_number_to_label


def clean_category(category):
    return category.strip().capitalize()


def load_vars(items):
    categories = {}

    count = 0
    for item in items:
        if load_var(item, categories):
            count += 1
    return count


def load_var(var_dict, categories):
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
        return False

    variable, created = CulturalVariable.objects.get_or_create(
        label=label, source=source)
    variable.name = var_dict['VarTitle']
    variable.codebook_info = var_dict['VarDefinition']
    variable.data_type = var_dict['VarType']

    for c in map(clean_category, var_dict['IndexCategory'].split(',')):
        index_category = categories.get(c)
        if not index_category:
            index_category = categories[c] = CulturalCategory.objects.create(name=c)
            logging.info("Created CulturalCategory: %s" % c)

        if index_category not in variable.index_categories.all():
            variable.index_categories.add(index_category)

    variable.save()
    logging.info("Created CulturalVariable: %s" % label)
    logging.info("Saved variable %s - %s" % (label, variable.name))
    return True


def load_codes(items):
    count = 0
    for row in items:
        dataset = row['Dataset']
        code = row['Code']
        id = row['VarID']
        description = row['CodeDescription']
        short_description = row['ShortName']
        
        if dataset == 'EA':
            label = eavar_number_to_label(id)
        elif dataset == 'LRB':
            label = bfvar_number_to_label(id)
        else:
            logging.warn("Unknown dataset, skipping row %s" % row)
            continue

        variable = CulturalVariable.objects.get(label=label)
        if variable:
            code_description, created = CulturalCodeDescription.objects.get_or_create(
                variable=variable, code=code)
            code_description.description = description
            code_description.short_description = short_description
            code_description.save()
            logging.info("Created CulturalCodeDescription: %s" % code_description)
            count += 1
        else:
            logging.warn("Missing variable in database: %s" % label)
    return count
