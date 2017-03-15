# coding: utf8
from __future__ import unicode_literals
import logging

from dplace_app.models import Society, GeographicRegion, SocietyRelation

from sources import get_source


def society_locations(repos):
    societies = {s.ext_id: s for s in Society.objects.all()}
    regions = {r.region_nam: r for r in GeographicRegion.objects.all()}

    count = 0
    for item in repos.read_csv('csv', 'society_locations.csv', dicts=True):
        society = societies.get(item['soc_id'])
        if not society:
            logging.warn("No matching society found for %s" % item)
            continue

        region = regions.get(item['region'])
        if not region:
            logging.warn("No matching region found for %s" % item)
        else:
            society.region = region
        society.save()
        count += 1
    return count


def load_society_relations(repos):
    count = 0
    societies = {s.ext_id: s for s in Society.objects.all()}
    for ds in repos.datasets:
        for item in ds.society_relations:
            if item.id in societies:
                for rel in item.related:
                    if rel.id in societies:
                        SocietyRelation.objects.create(
                            from_society=societies[item.id], to_society=societies[rel.id])
                        count += 1
                    elif rel.dataset == 'CHIRILA':
                        societies[item.id].chirila_link = rel.name
                        societies[item.id].save()
    return count


def load_societies(repos):
    societies = []
    for ds in repos.datasets:
        for item in ds.societies:
            lat, lon, olat, olon = None, None, None, None
            try:
                lat, lon = map(float, [item.Lat, item.Long])
            except (TypeError, ValueError):
                logging.warn("Unable to create coordinates for %s" % item)
            try:
                olat, olon = map(float, [item.origLat, item.origLong])
            except (TypeError, ValueError):
                logging.warn("Unable to create original coordinates for %s" % item)

            societies.append(Society(
                ext_id=item.id,
                xd_id=item.xd_id,
                original_name=item.ORIG_name_and_ID_in_this_dataset,
                name=item.pref_name_for_society,
                source=get_source(ds),
                alternate_names=item.alt_names_by_society,
                focal_year=item.main_focal_year,
                hraf_link=item.HRAF_name_ID,
                #chirila_link=item.CHIRILA_society_equivalent,
                latitude=lat,
                longitude=lon,
                original_latitude=olat,
                original_longitude=olon,
            ))
            logging.info("Saving society %s" % item.id)

    Society.objects.bulk_create(societies)

    #
    # TODO: load cross-dataset relations!
    #
    return len(societies)
