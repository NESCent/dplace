#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import chain, groupby
from time import time
from functools import partial

import django
django.setup()

from django.db import transaction
from django.conf import settings
from clldutils.dsv import reader
from clldutils.path import Path
from clldutils.text import split_text
from clldutils import jsonlib
import attr

from load.util import configure_logging
from load.society import society_locations, load_societies
from load.environmental import load_environmental, load_environmental_var
from load.geographic import load_regions
from load.tree import load_trees, tree_names, prune_trees
from load.variables import load_vars
from load.values import load_data
from load.sources import load_references
from load.glottocode import load_languages

DATA_DIR = Path(__file__).parent.parent.joinpath('datasets')
comma_split = partial(split_text, separators=',', strip=True)
semicolon_split = partial(split_text, separators=';', strip=True)


def valid_enum_member(choices, instance, attribute, value):
    if value not in choices:
        raise ValueError(value)


def _var_label(dataset, var_id):
    return "{0}{1:0>3}".format({'Binford': 'B'}.get(dataset, dataset), var_id)


@attr.s
class Variable(object):
    dataset = attr.ib()
    category = attr.ib(convert=lambda s: [c.capitalize() for c in comma_split(s)])
    id = attr.ib()
    title = attr.ib()
    definition = attr.ib()
    type = attr.ib(
        validator=partial(valid_enum_member, ['Continuous', 'Categorical', 'Ordinal']))
    units = attr.ib()
    source = attr.ib()
    changes = attr.ib()
    notes = attr.ib()
    codes = attr.ib(default=attr.Factory(list))

    @property
    def label(self):
        return _var_label(self.dataset, self.id)


@attr.s
class Data(object):
    dataset = attr.ib()
    soc_id = attr.ib()
    sub_case = attr.ib()
    year = attr.ib()
    var_id = attr.ib()
    code = attr.ib()
    comment = attr.ib()
    references = attr.ib(convert=semicolon_split)
    source_coded_data = attr.ib()
    admin_comment = attr.ib()

    @property
    def var_label(self):
        return _var_label(self.dataset, self.var_id)


class Dataset(object):
    def __init__(self, spec):
        self.spec = spec
        self.id = spec['id']
        self.dir = DATA_DIR.joinpath('datasets', self.id)

    def _items(self, what, **kw):
        fname = self.dir.joinpath('{0}.csv'.format(what))
        return list(reader(fname, **kw)) if fname.exists() else []

    @property
    def data(self):
        return [Data(**d) for d in self._items('data', dicts=True)]

    @property
    def references(self):
        return self._items('references', namedtuples=True)

    @property
    def societies(self):
        return self._items('societies', namedtuples=True)

    @property
    def variables(self):
        codes = {vid: list(c) for vid, c in groupby(
            sorted(self._items('codes', namedtuples=True), key=lambda c: c.var_id),
            lambda c: c.var_id)}
        return [
            Variable(dataset=self.id, codes=codes.get(v['id'], []), **v)
            for v in self._items('variables', dicts=True)]


def main():  # pragma: no cover
    configure_logging()

    datasets = [Dataset(r) for r in
                reader(DATA_DIR.joinpath('datasets', 'index.csv'), dicts=True)]
    for spec in [
        (load_societies, datasets),
        (load_regions, jsonlib.load(DATA_DIR.joinpath('geo', 'level2.json'))),
        (society_locations, DATA_DIR.joinpath('csv', 'society_locations.csv')),
        (load_vars, datasets),
        (
            load_languages,
            datasets,
            {l.id: l for l in
             reader(DATA_DIR.joinpath('csv', 'glottolog.csv'), namedtuples=True)}),
        (load_references, datasets),
        (load_data, datasets),
        (
            load_environmental_var,
            reader(DATA_DIR.joinpath('csv', 'environmentalVariableList.csv'), dicts=True)
        ),
        (
            load_environmental,
            reader(DATA_DIR.joinpath('csv', 'environmental_data.csv'), dicts=True)),
        (load_trees, DATA_DIR.joinpath()),
        (tree_names, DATA_DIR.joinpath()),
        (prune_trees,),
    ]:
        with transaction.atomic():
            loader, args = spec[0], spec[1:]
            print("%s..." % loader.__name__)
            start = time()
            res = loader(*args)
            print("%s loaded in %s secs" % (res, time() - start))


if __name__ == '__main__':  # pragma: no cover
    main()
    sys.exit(0)
