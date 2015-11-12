# -*- coding: utf-8 -*-
# __author__ = 'Stef'
# used to load variables

import csv
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.load.isocode import get_isocode
from dplace_app.models import *
from environmental import iso_from_code
from sources import get_source
# TODO: figure out how to deal with focal year.

def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)
    
def clean_category(category):
    return category.strip().capitalize()

def load_vars(var_dict):
    """
    Load variables from VariableList.csv
    """
    dataset = var_dict['Dataset'].strip()
    index_categories = [clean_category(x) for x in var_dict['IndexCategory'].split(',')]
    ea_id = var_dict['VarID']
    name = var_dict['VarTitle']
    description = var_dict['VarDefinition']
    datatype = var_dict['VarType']
    
    if dataset=='EA':
        ea_label = eavar_number_to_label(ea_id)
        variable, created = VariableDescription.objects.get_or_create(label=ea_label, source=get_source("EA"))
        variable.name = name
        variable.codebook_info = description
        variable.data_type = datatype
        for i in variable.index_categories.all():
            variable.index_categories.remove(i)
        for c in index_categories:
            index_category, created = VariableCategory.objects.get_or_create(name=c)
            variable.index_categories.add(index_category)
        variable.save()
        print "Saved variable %s - %s" % (ea_label, name)
        
