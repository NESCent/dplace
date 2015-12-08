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
from variables import clean_category
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
    ext_id = val_row['soc_id']
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA values for %s but did not find an existing Society object, skipping" % ext_id
        return
        
    variable = get_variable(val_row['VarID'].strip())
    value = val_row['Code'].strip()
    comment = val_row['Comment'].strip()
    references = val_row['References'].strip().split(";")   
    focal_year = val_row['Year'].strip()
    
    if variable is None:
        print "Could not find variable %s for society %s" % (val_row['VarID'], society)
        return

