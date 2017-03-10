# -*- coding: utf-8 -*-
import logging

from dplace_app.models import (
    CulturalVariable, CulturalCategory, CulturalCodeDescription,
    EnvironmentalCategory, EnvironmentalVariable,
)
from sources import get_source


def clean_category(category):
    return category.strip().capitalize()


def load_vars(datasets):
    categories, count = {}, 0
    for ds in datasets:
        for var in ds.variables:
            count += load_var(ds, var, categories)
    return count


def load_var(ds, var, categories):
    if ds.type == 'cultural':
        variable = CulturalVariable.objects.create(
            name=var.title,
            codebook_info=var.definition,
            data_type=var.type,
            units=var.units,
            label=var.label,
            source=get_source(ds))
        cat_class = CulturalCategory
    else:
        if len(var.title) > 150:
            print(len(var.title), var.title)
        if var.type != 'Continuous':
            return 0
        variable = EnvironmentalVariable.objects.create(
            var_id=var.id,
            name=var.title,
            units=var.units,
            codebook_info=var.definition)
        cat_class = EnvironmentalCategory

    for c in var.category:
        index_category = categories.get((ds.type, c))
        if not index_category:
            index_category = categories[(ds.type, c)] = cat_class.objects.create(name=c)
            logging.info("Created %s: %s" % (cat_class.__name__, c))

        if ds.type == 'cultural':
            if index_category not in variable.index_categories.all():
                variable.index_categories.add(index_category)
        else:
            variable.category = index_category

    for code in var.codes:
        code_description, created = CulturalCodeDescription.objects.get_or_create(
            variable=variable, code=code.code)
        code_description.description = code.description
        code_description.short_description = code.name
        code_description.save()
        logging.info(
            ("Created CulturalCodeDescription: %s" % code_description).decode('utf8'))

    variable.save()
    logging.info("Created CulturalVariable: %s" % var.label)
    logging.info("Saved variable %s - %s" % (var.label, variable.name))
    return 1
