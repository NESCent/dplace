# coding: utf8
from __future__ import unicode_literals
import logging

from django.conf import settings

from dplace_app.models import Society, GeographicRegion

from dplace_app.load.util import delete_all
from dplace_app.load.sources import get_source


def society_locations(items):
    societies = {s.ext_id: s for s in Society.objects.all()}
    regions = {r.region_nam: r for r in GeographicRegion.objects.all()}
    
    count = 0
    for item in items:
        if item['dataset'] not in settings.DATASETS:
            continue
        society = societies.get(item['soc_id'])
        if not society:
            logging.warn("No matching society found for %s" % item)
            continue

        try:
            society.latitude, society.longitude = map(
                float, [item['Lat'], item['Long']])
        except (TypeError, ValueError):
            logging.warn("Unable to create coordinates for %s" % item)
        
        try:
            society.original_latitude, society.original_longitude = map(
                float, [item['origLat'], item['origLong']])
        except (TypeError, ValueError):
            logging.warn("Unable to create original coordinates for %s" % item)

        region = regions.get(item['region'])
        if not region:
            logging.warn("No matching region found for %s" % item)
        else:
            society.region = region
        society.save()
        count += 1
    return count


def load_societies(items):
    society_links = [
        'SCCS_society_equivalent',
        'WNAI_society_equivalent1',
        'WNAI_society_equivalent2',
        'WNAI_society_equivalent3',
        'WNAI_society_equivalent4',
        'WNAI_society_equivalent5',
    ]
    delete_all(Society)
    societies = []
    for item in items:
        societies.append(Society(
            ext_id=item['soc_id'],
            xd_id=item['xd_id'],
            original_name=item['ORIG_name_and_ID_in_this_dataset'],
            name=item['pref_name_for_society'], 
            source=get_source(item['dataset']),
            alternate_names=item['alt_names_by_society'],
            focal_year=item['main_focal_year'],
            hraf_link=item['HRAF_name_ID'],
            chirila_link=item['CHIRILA_society_equivalent']
        ))
        for key in society_links:
            value = item.get(key)
            if value:
                ext_id = value.split('(')[len(value.split('(')) - 1]
                society = Society(
                    ext_id=ext_id[0:len(ext_id) - 1],
                    xd_id=item['xd_id'],
                    original_name=value,
                    name=item['pref_name_for_society'],
                    alternate_names=item['alt_names_by_society'],
                    focal_year=item['main_focal_year'],
                    source=get_source(key[0:key.find('_')])
                )
                if society.ext_id not in [x.ext_id for x in societies]:
                    societies.append(society)
                    logging.info("Saving society %s" % society.ext_id)

        logging.info("Saving society %s" % item)

    Society.objects.bulk_create(societies)
    return len(societies)
