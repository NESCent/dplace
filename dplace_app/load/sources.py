# -*- coding: utf-8 -*-
# __author__ = 'stef'

import csv
from dplace_app.models import Source

_SOURCE_CACHE = {}  
def get_source(source='EA'):
    if source in _SOURCE_CACHE:
        return _SOURCE_CACHE[source]
    
    if source == 'EA':
        try:
            o = Source.objects.get(year="1999", author="Murdock et al.")
        except Source.DoesNotExist:
            o = Source.objects.create(
                year="1999",
                author="Murdock et al.",
                reference="Murdock, G. P., R. Textor, H. Barry, III, D. R. White, J. P. Gray, and W. T. Divale. 1999. Ethnographic Atlas. World Cultures 10:24-136 (codebook)",
            )
        o.name = "Ethnographic Atlas"
        o.save()
    elif source == 'Binford':
        try:
            o = Source.objects.get(year="2001", author="Binford")
        except Source.DoesNotExist:
            o = Source.objects.create(
                year="2001",
                author="Binford",
                reference="Binford, L. 2001. Constructing Frames of Reference: An Analytical Method for Archaeological Theory Building Using Hunter-gatherer and Environmental Data Sets. University of California Press",
            )
        o.name = "Binford Hunter-Gatherer"
        o.save()
    else:
        raise ValueError("Unknown Source: %s" % source)
    _SOURCE_CACHE[source] = o
    return o

SHORT_REF_COLUMN    = 0
COMPLETE_REF_COLUMN = 1
def load_references(csvfile=None):
    csv_reader = csv.reader(csvfile)
    for dict_row in csv_reader:
        #skip rows that don't have two columns
        if len(dict_row) != 2:
            continue
        #skip headers
        if dict_row[SHORT_REF_COLUMN] == 'ReferenceShort' and dict_row[COMPLETE_REF_COLUMN] == 'ReferenceComplete':
            continue

        #ReferenceShort field is in the format Author, Year
        #ref_short = array containing [Author, Year]
        try:
            ref_short = dict_row[SHORT_REF_COLUMN].strip().split(",")
            ref_complete = dict_row[COMPLETE_REF_COLUMN].strip()
            try:
                author = ref_short[0].strip()
                year = ref_short[1].strip()
                reference, created = Source.objects.get_or_create(author=author, year=year, reference=ref_complete)
                reference.save()
                if created:
                    print "Saved new reference %s" % reference
            except IndexError:
                print "No author and/or year for %s" % str(dict_row)
        except:
            print "Could not save reference for row %s" % str(dict_row)
    