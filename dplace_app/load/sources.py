# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from dplace_app.models import Source


_SOURCE_CACHE = {}  
SOURCE_DATA = {
    'EA': dict(
        year="1999",
        author="Murdock et al.",
        reference="Murdock, G. P., R. Textor, H. Barry, III, D. R. White, J. P. Gray, and W. T. Divale. 1999. Ethnographic Atlas. World Cultures 10:24-136 (codebook)",
        name="Ethnographic Atlas",
    ),
    'Binford': dict(
        year="2001",
        author="Binford",
        reference="Binford, L. 2001. Constructing Frames of Reference: An Analytical Method for Archaeological Theory Building Using Hunter-gatherer and Environmental Data Sets. University of California Press",
        name="Binford Hunter-Gatherer",
    ),
}


def get_source(source='EA'):
    if source not in _SOURCE_CACHE:
        if source not in SOURCE_DATA:
            raise ValueError("Unknown Source: %s" % source)

        data = SOURCE_DATA[source]
        try:
            o = Source.objects.get(year=data['year'], author=data['author'])
        except Source.DoesNotExist:
            o = Source.objects.create(**data)
            o.save()
        _SOURCE_CACHE[source] = o
    return _SOURCE_CACHE[source]


def load_references(items):
    count = 0
    for row in items:
        # skip rows that don't have two columns
        if len(row) != 2:
            continue

        # ReferenceShort field is in the format Author, Year
        try:
            ref_short = row['ReferenceShort'].split(",")
            try:
                reference, created = Source.objects.get_or_create(
                    author=ref_short[0].strip(),
                    year=ref_short[1].strip(),
                    reference=row['ReferenceComplete'])
                if created:
                    count += 1
                    logging.info("Saved new reference %s (%s)"
                                 % (reference.author, reference.year))
            except IndexError:
                logging.warn("No author and/or year for %s" % str(row))
        except Exception as e:
            logging.warn("Could not save reference for row %s: %e"
                         % (str(row), e))
    return count
