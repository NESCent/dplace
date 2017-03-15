# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from clldutils.text import split_text
from dplace_app.models import Source

_SOURCE_CACHE = {}


def get_source(ds):
    dsid = getattr(ds, 'id', ds)
    if dsid not in _SOURCE_CACHE:
        try:
            o = Source.objects.get(year=ds.year, author=ds.author)
        except Source.DoesNotExist:
            o = ds.as_source()
            o.save()
        _SOURCE_CACHE[ds.id] = o
    return _SOURCE_CACHE[dsid]


def load_references(repos):
    keys = set()
    for ds in repos.datasets:
        for r in ds.references:
            if ':' in r.key:
                # skip keys with page numbers.
                continue

            # key is in the format Author, Year
            try:
                author, year = split_text(r.key, separators=',', strip=True)
                if (author, year) not in keys:
                    keys.add((author, year))
                    reference = Source.objects.create(
                        author=author, year=year, reference=r.citation)
                    logging.info("Saved new reference %s (%s)"
                                 % (reference.author, reference.year))
            except Exception as e:  # pragma: no cover
                logging.warn("Could not save reference for row %s: %s" % (str(r), e))
    return len(keys)
