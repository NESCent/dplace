# -*- coding: utf-8 -*-
import logging
import re

from django.db import connection

from dplace_app.models import (
    Society, Source, CulturalValue, CulturalVariable, CulturalCodeDescription,
)
from sources import get_source
from util import eavar_number_to_label, bfvar_number_to_label


BINFORD_REF_PATTERN = re.compile('(?P<author>[^0-9]+)(?P<year>[0-9]{4}a-z?):')


def load_data(items):
    refs = []
    objs = []
    kw = dict(
        societies={s.ext_id: s for s in Society.objects.all()},
        sources={(s.author, s.year): s for s in Source.objects.all()},
        variables={vd.label: vd for vd in CulturalVariable.objects.all()},
        descriptions={(vcd.variable_id, vcd.code): vcd
                      for vcd in CulturalCodeDescription.objects.all()})

    #
    # To speed up the data load, we first delete all relevant objects, and then recreate
    # them using bulk_create.
    # Note that since we must rebuild the association table between values and sources
    # as well, we must keep control over the inserted primary keys for values. To do so,
    # we reset the id sequence as well.
    #
    CulturalValue.objects.all().delete()
    with connection.cursor() as c:
        for table in ['variablecodedvalue_references', 'variablecodedvalue']:
            c.execute("ALTER SEQUENCE dplace_app_%s_id_seq RESTART WITH 1" % table)

    inserted = set()
    pk = 0
    for i, item in enumerate(items):
        res = _load_data(item, **kw)
        if res:
            key = (res[0]['variable'].id, res[0]['society'].id, res[0]['coded_value'])
            if key in inserted:
                logging.warn("duplicate value %s" % item)
            else:
                inserted.add(key)
                pk += 1
                objs.append(CulturalValue(**res[0]))
                refs.extend([(pk, sid) for sid in res[1] or []])

    CulturalValue.objects.bulk_create(objs, batch_size=1000)

    with connection.cursor() as c:
        c.executemany(
            """\
INSERT INTO dplace_app_culturalvalue_references (culturalvalue_id, source_id)
VALUES (%s, %s)""",
            refs)
    return pk


def _load_data(val_row, societies=None, sources=None, variables=None, descriptions=None):
    ext_id = val_row.get('soc_id')
    if ext_id not in societies:
        logging.warn(
            "Attempting to load values for %s but no Society object exists, skipping"
            % ext_id)
        return

    society = societies[ext_id]
    variable_id = val_row['VarID']

    if val_row['Dataset'] == 'EA':
        source = get_source("EA")
        label = eavar_number_to_label(variable_id)
    elif val_row['Dataset'] == 'LRB':
        source = get_source("Binford")
        label = bfvar_number_to_label(variable_id)
    else:
        logging.warn("Could not determine dataset source for row %s, skipping" % str(val_row))
        return

    variable = variables.get(label)
    if variable is None:
        logging.warn("Could not find variable %s for society %s" % (variable_id, society.name))
        return

    v = dict(
        variable=variable,
        society=society,
        source=source,
        coded_value=val_row['Code'],
        code=descriptions.get((variable.id, val_row['Code'].strip())),
        focal_year=val_row['Year'],
        comment=val_row['Comment'],
        subcase=val_row['SpecRef'])

    refs = set()
    for r in val_row['References'].split(";"):
        r = r.strip()
        author, year = None, None
        m = BINFORD_REF_PATTERN.match(r)
        if m:
            author, year = m.group('author').strip(), m.group('year')
        else:
            ref_short = r.split(",")
            if len(ref_short) == 2:
                author = ref_short[0].strip()
                year = ref_short[1].strip()
        if author and year:
            ref = sources.get((author, year))
            if ref:
                refs.add(ref.id)
            else:
                logging.warn(
                    "Could not find reference %s (%s) in database, skipping reference"
                    % (author, year))
    return v, refs
