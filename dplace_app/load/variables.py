# -*- coding: utf-8 -*-
import logging

from dplace_app.models import CulturalVariable, CulturalCategory, CulturalCodeDescription

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
    variable, created = CulturalVariable.objects.get_or_create(
        label=var.label, source=get_source(ds))
    variable.name = var.title
    variable.codebook_info = var.definition
    variable.data_type = var.type
    variable.units = var.units

    for c in var.category:
        index_category = categories.get(c)
        if not index_category:
            index_category = categories[c] = CulturalCategory.objects.create(name=c)
            logging.info("Created CulturalCategory: %s" % c)

        if index_category not in variable.index_categories.all():
            variable.index_categories.add(index_category)

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
