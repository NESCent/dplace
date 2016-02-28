# coding: utf8
from __future__ import unicode_literals
import logging

from dplace_app.models import Society, GeographicRegion

from util import delete_all
from sources import get_source


def society_locations(items):
    societies = {s.ext_id: s for s in Society.objects.all()}
    regions = {r.region_nam: r for r in GeographicRegion.objects.all()}

    count = 0
    for item in items:
        society = societies.get(item['soc_id'])
        if not society:
            logging.warn("No matching society found for %s" % item)
            continue

        try:
            society.latitude, society.longitude = map(
                float, [item['Latitude'], item['Longitude']])
        except (TypeError, ValueError):
            logging.warn("Unable to create coordinates for %s" % item)

        region = regions.get(item['region'])
        if not region:
            logging.warn("No matching region found for %s" % item)
        else:
            society.region = region
        society.save()
        count += 1
    return count

def load_societies(items):
    delete_all(Society)
    societies = []
    for item in items:
        if item['dataset'] == 'EA':
            source = get_source("EA")
        elif item['dataset'] == 'Binford':
            source = get_source("Binford")
        #elif item['dataset'] == 'SCCS':
        #    source = get_source("SCCS")
        #elif item['dataset'] == 'Jorgensen':
        #    source = get_source("WNAI")       
        else:
            logging.warn(
                "Could not determine source for row %s, skipping" % item
            )
            continue
        
        societies.append(Society(
            ext_id=item['soc_id'],
            xd_id=item['xd_id'],
            name=item['pref_name_for_society'], #previously ORIG_name -- not sure if we need that one, so for now we'll just save the preferred name
            source=source,
            alternate_names=item['alt_names_by_society'],
            focal_year=item['main_focal_year'],
        ))
        
        if item['SCCS_society_equivalent']: # need to check to make sure the society isn't already appended to the array...
            source = get_source("SCCS")
            societies.append(Society(
                ext_id=item['SCCS_society_equivalent'][item['SCCS_society_equivalent'].find("(")+1:item['SCCS_society_equivalent'].find(")")],
                xd_id=item['xd_id'],
                name=item['pref_name_for_society'],
                alternate_names=item['alt_names_by_society'],
                focal_year=item['main_focal_year']
            ))
            
        logging.info("Saving society %s" % item)
    Society.objects.bulk_create(societies)
    return len(societies)
    
def link_societies(items):
    '''Reads from header_data csv files'''
    societies = []
    for item in items:
        if item['HRAF_name_ID']:
            source = get_source("EHRAF")
            societies.append(Society(
            
            ))
    
    