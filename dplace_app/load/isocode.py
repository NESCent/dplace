# -*- coding: utf-8 -*-
# __author__ = 'dan'
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *

def get_value(dict,possible_keys):
    '''
    Get a value from a dictionary, searching the possible keys in order
    '''
    for key in possible_keys:
        if key in dict.keys():
            return dict[key]
    return None

def get_isocode(dict):
    '''
    ISO Code may appear in 'ISO' column (17th Ed Missing ISO codes)
    or the 'ISO 693-3 code' column (17th Ed - ISO 693-3 - current)
    '''
    return get_value(dict,('ISO','ISO 693-3 code','ISO693_3'))

def load_isocode(iso_dict):
    code = get_isocode(iso_dict)
    if code is None:
        print "ISO Code not found in row, skipping"
        return None
    if len(code) > 3:
        print "ISO Code '%s' too long, skipping" % code
        return None
    return ISOCode.objects.get_or_create(iso_code=code)

def load_iso_lat_long(iso_dict):
    code = get_isocode(iso_dict)
    found_code = None
    try:
        found_code = ISOCode.objects.get(iso_code=code)
    except ObjectDoesNotExist:
        print "Tried to attach Lat/Long to ISO Code %s but code not found" % code
        return None
    location = Point(float(iso_dict['LMP_LON']),float(iso_dict['LMP_LAT']))
    found_code.location = location
    try:
        found_code.save()
    except:
        print "Unable to attach location to iso code"
        return None
    return found_code
