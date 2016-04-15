# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging
from dplace_app.models import Source

_SOURCE_CACHE = {}
SOURCE_DATA = {
    'EA': dict(
        year="1999",
        author="Murdock et al.",
        reference="Murdock, G. P., R. Textor, H. Barry, III, D. R. White, J. P. Gray, "
                  "and W. T. Divale. 1999. Ethnographic Atlas. World Cultures 10:24-136 "
                  "(codebook)",
        name="Ethnographic Atlas",
    ),
    'Binford': dict(
        year="2001",
        author="Binford",
        reference="Binford, L. 2001. Constructing Frames of Reference: An Analytical "
                  "Method for Archaeological Theory Building Using Hunter-gatherer and "
                  "Environmental Data Sets. University of California Press",
        name="Binford Hunter-Gatherer",
    ),
    
    # data from these databases are not stored in our database, but the easiest way to link our societies to external databases is to do this, rather than create new fields for the Society model
    'SCCS': dict(
        year="1969",
        author="Murdock",
        reference=""
    ),
    'WNAI': dict(
        year="1966",
        author="Jorgensen",
        reference=""
    ),
    'Jorgensen': dict(
        year="1966",
        author="Jorgensen",
        reference=""
    )
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
    keys = set()
    for row in items:
        # skip rows that don't have two columns
        if len(row) != 2:
            continue

        short = row.get('ReferenceShort', row.get('ShortRef_w_AND_wout_pp', ''))
        complete = row.get('ReferenceComplete', row.get('LongRef', ''))
        if ':' in short:
            # skip short refs with page numbers.
            continue

        # ReferenceShort field is in the format Author, Year
        try:
            ref_short = short.split(",")
            try:
                author, year = ref_short[0].strip(), ref_short[1].strip()
                if (author, year) not in keys:
                    keys.add((author, year))
                    reference = Source.objects.create(
                        author=ref_short[0].strip(),
                        year=ref_short[1].strip(),
                        reference=complete)
                    logging.info("Saved new reference %s (%s)"
                                 % (reference.author, reference.year))
            except IndexError:
                logging.warn("No author and/or year for %s" % str(row))
        except Exception as e:  # pragma: no cover
            logging.warn(
                "Could not save reference for row %s: %s" % (str(row), e)
            )
    return len(keys)
