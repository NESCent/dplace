# -*- coding: utf-8 -*-
# __author__ = 'stef'

import csv
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.models import *
from sources import get_source

def ea_soc_to_xd_id(dict_row):
    soc_id = dict_row['soc_id']
    xd_id = dict_row['xd_id']
    try:
        society = Society.objects.get(ext_id=soc_id)
        society.xd_id = xd_id
        society.save()
    except ObjectDoesNotExist:
        "Warning: Unable to find society %s" % soc_id
        return

def load_ea_society(society_dict):
    ext_id = society_dict['soc_id'].strip()
    xd_id = society_dict['xd_id'].strip()
    soc_name = society_dict['soc_name'].strip()
    source = get_source('EA')
    focal_year = society_dict['main_focal_year'].strip()
    alternate_names = society_dict['alternate_names'].strip()
    
    society, created = Society.objects.get_or_create(ext_id=ext_id)
    society.xd_id = xd_id
    society.source = source
    society.name = soc_name
    society.alternate_names = alternate_names
    society.focal_year = focal_year
    
    print "Saving society %s" % society
    society.save()
    
def society_locations(dict_row):
    '''
    Locations for societies from EA_Binford_Lat_Long.csv.
    '''
    soc_id = dict_row['soc_id']
    lat_val = dict_row['Latitude']
    long_val = dict_row['Longitude']
    
    try:
        society = Society.objects.get(ext_id=soc_id)
        try:
            location = Point(
                float(long_val),
                float(lat_val)
            )
            society.location = location
        except ValueError:
            print "Unable to create Point from (%s,%s) for society %s" % (long_val, lat_val, society)
        society.save()
    except ObjectDoesNotExist:
        print "No society with ID %s in database, skipping" % soc_id
