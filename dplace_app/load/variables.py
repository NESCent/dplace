# -*- coding: utf-8 -*-
import logging
from dplace_app.models import CulturalVariable, CulturalCategory, CulturalCodeDescription

from sources import get_source
from util import var_number_to_label


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
    label = var_number_to_label(var_dict['Dataset'], var_dict['VarID'])
    variable, created = CulturalVariable.objects.get_or_create(
        label=label, source=get_source(var_dict['Dataset']))
    variable.name = var_dict['VarTitle']
    variable.codebook_info = var_dict['VarDefinition']
    variable.data_type = var_dict['VarType']
    assert variable.data_type in ['Continuous', 'Categorical', 'Ordinal']
    variable.units = "" if 'Units' not in var_dict else var_dict['Units']

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
        label = var_number_to_label(row['Dataset'], row['VarID'])
        variable = CulturalVariable.objects.filter(label=label).first()
        if variable:
            code_description, created = CulturalCodeDescription.objects.get_or_create(
                variable=variable, code=row['Code'])
            code_description.description = row['CodeDescription']
            code_description.short_description = row['ShortName']
            code_description.save()
            logging.info(
                ("Created CulturalCodeDescription: %s" % code_description).decode('utf8'))
            count += 1
        else:
            logging.warn("Missing variable in database: %s" % label)
    return count
