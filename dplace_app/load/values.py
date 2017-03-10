# -*- coding: utf-8 -*-
import logging
import re
from operator import attrgetter

from django.db import connection
from django.conf import settings

from dplace_app.models import (
    Society, Source, CulturalValue, CulturalVariable, CulturalCodeDescription,
    EnvironmentalVariable, EnvironmentalValue,
)
from sources import get_source


BINFORD_REF_PATTERN = re.compile('(?P<author>[^0-9]+)(?P<year>[0-9]{4}a-z?):')


def load_data(datasets):
    refs = []
    societies = {s.ext_id: s for s in Society.objects.all()}
    kw = dict(
        sources={(s.author, s.year): s for s in Source.objects.all()},
        descriptions={(vcd.variable_id, vcd.code): vcd
                      for vcd in CulturalCodeDescription.objects.all()})

    #
    # To speed up the data load, we first delete all relevant objects, and then recreate
    # them using bulk_create.
    # Note that since we must rebuild the association table between values and sources
    # as well, we must keep control over the inserted primary keys for values. To do so,
    # we reset the id sequence as well.
    #
    #CulturalValue.objects.all().delete()
    #with connection.cursor() as c:
    #    for table in ['culturalvalue_references', 'culturalvalue']:
    #        c.execute("ALTER SEQUENCE dplace_app_%s_id_seq RESTART WITH 1" % table)

    for dstype, var_cls, var_id_attr, val_cls, val_var_id_attr in [
        ('cultural', CulturalVariable, 'label', CulturalValue, 'var_label'),
        ('environmental', EnvironmentalVariable, 'var_id', EnvironmentalValue, 'var_id')
    ]:
        var_id_attr = attrgetter(var_id_attr)
        val_var_id_attr = attrgetter(val_var_id_attr)
        variables = {var_id_attr(var): var for var in var_cls.objects.all()}
        objs = []
        pk = 0
        for ds in datasets:
            if (ds.id not in settings.DATASETS) or (ds.type != dstype):
                continue
            for item in ds.data:
                vid = val_var_id_attr(item)
                v, _refs = _load_data(
                    ds, item, societies[item.soc_id], variables[vid], **kw)
                pk += 1
                objs.append(val_cls(**v))
                refs.extend([(pk, sid) for sid in _refs or []])

        val_cls.objects.bulk_create(objs, batch_size=1000)

    with connection.cursor() as c:
        c.executemany(
            """\
INSERT INTO dplace_app_culturalvalue_references (culturalvalue_id, source_id)
VALUES (%s, %s)""",
            refs)
    return CulturalValue.objects.count() + EnvironmentalValue.objects.count()


def _load_data(ds, val, society, variable, sources=None, descriptions=None):
    v = dict(
        variable=variable,
        comment=val.comment,
        society=society,
        source=get_source(val.dataset))
    if ds.type == 'cultural':
        v.update(
            coded_value=val.code,
            code=descriptions.get((variable.id, val.code)),
            focal_year=val.year,
            subcase=val.sub_case)
        if variable.data_type == 'Continuous' and val.code and val.code != 'NA':
            v['coded_value_float'] = float(val.code)
    else:
        v['value'] = float(val.code)

    refs = set()
    if ds.type == 'cultural':
        for r in val.references:
            author, year = None, None
            m = BINFORD_REF_PATTERN.match(r)
            if m:
                author, year = m.group('author').strip(), m.group('year')
                if author.endswith(','):
                    author = author[:-1].strip()
            else:
                ref_short = r.split(",")
                if len(ref_short) == 2:
                    author = ref_short[0].strip()
                    year = ref_short[1].strip().split(':')[0]
            if author and year:
                ref = sources.get((author, year))
                if ref:
                    refs.add(ref.id)
                else:  # pragma: no cover
                    logging.warn(
                        "Could not find reference %s, %s in database, skipping reference"
                        % (author, year))
    return v, refs
