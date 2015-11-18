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

def _unicode_damnit(var):
    return var.decode('latin1').encode('utf8')

def load_bf_society(society_dict):
    ext_id = society_dict['soc_id'].strip()
    xd_id = society_dict['xd_id'].strip()
    soc_name = society_dict['soc_name'].strip()
    source = get_source('Binford')
    focal_year = society_dict['main_focal_year'].strip()
    alternate_names = society_dict['alternate_names'].strip()
    
    society, created = Society.objects.get_or_create(ext_id=ext_id)
    society.xd_id = xd_id
    society.name = soc_name
    society.source = source
    society.alternate_names = alternate_names
    society.focal_year = focal_year
    
    print "Saving society %s" % society
    society.save()

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
