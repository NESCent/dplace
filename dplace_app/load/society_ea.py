# -*- coding: utf-8 -*-
import logging
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import Society

from sources import get_source
from util import load_society


def ea_soc_to_xd_id(dict_row):
    soc_id = dict_row['soc_id']
    xd_id = dict_row['xd_id']
    try:
        society = Society.objects.get(ext_id=soc_id)
        society.xd_id = xd_id
        society.save()
    except ObjectDoesNotExist:
        logging.warn("Warning: Unable to find society %s" % soc_id)
        return


def load_ea_society(society_dict):
    return load_society(society_dict, get_source('EA'))


def society_locations(dict_row):
    '''
    Locations for societies from EA_Binford_Lat_Long.csv.
    '''
    lat_val = dict_row['Latitude']
    long_val = dict_row['Longitude']
    
    try:
        society = Society.objects.get(ext_id=dict_row['soc_id'])
        try:
            society.location = Point(float(long_val), float(lat_val))
            society.save()
            logging.info(
                "Added location (%s,%s) for society %s" % (long_val, lat_val, society))
        except ValueError:
            logging.warn(
                "Unable to create Point from (%s,%s) for society %s" %
                (long_val, lat_val, society))
    except ObjectDoesNotExist:
        logging.warn("No society with ID %(soc_id)s in database, skipping" % dict_row)
