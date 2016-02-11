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
        elif item['dataset'] == 'LRB':
            source = get_source("Binford")
        else:
            logging.warn(
                "Could not determine source for row %s, skipping" % item
            )
            continue

        societies.append(Society(
            ext_id=item['soc_id'],
            xd_id=item['xd_id'],
            name=item['soc_name'],
            source=source,
            alternate_names=item['alternate_names'],
            focal_year=item['main_focal_year'],
        ))
        logging.info("Saving society %s" % item)

    Society.objects.bulk_create(societies)
    return len(societies)
