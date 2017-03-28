#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import groupby
from time import time
from functools import partial
import re

import django
django.setup()

from django.db import transaction
from clldutils.dsv import reader
from clldutils.text import split_text
from clldutils.path import Path
from clldutils import jsonlib
import attr

from dplace_app.models import Source
from loader.util import configure_logging, load_regions
from loader.society import society_locations, load_societies, load_society_relations
from loader.phylogenies import load_phylogenies
from loader.variables import load_vars
from loader.values import load_data
from loader.sources import load_references
from loader.glottocode import load_languages

comma_split = partial(split_text, separators=',', strip=True, brackets={})
semicolon_split = partial(split_text, separators=';', strip=True, brackets={})


def valid_enum_member(choices, instance, attribute, value):
    if value not in choices:
        raise ValueError(value)


@attr.s
class Variable(object):
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


@attr.s
class Data(object):
    soc_id = attr.ib()
    sub_case = attr.ib()
    year = attr.ib()
    var_id = attr.ib()
    code = attr.ib()
    comment = attr.ib()
    references = attr.ib(convert=semicolon_split)
    source_coded_data = attr.ib()
    admin_comment = attr.ib()


@attr.s
class ObjectWithSource(object):
    id = attr.ib()
    name = attr.ib()
    year = attr.ib()
    author = attr.ib()
    reference = attr.ib()
    base_dir = attr.ib()

    @property
    def dir(self):
        return self.base_dir.joinpath(self.id)

    def as_source(self):
        return Source.objects.create(
            **{k: getattr(self, k) for k in 'year author name reference'.split()})


@attr.s
class RelatedSociety(object):
    dataset = attr.ib(convert=lambda s: s.strip())
    name = attr.ib(convert=lambda s: s.strip())
    id = attr.ib(convert=lambda s: s.strip())

    @classmethod
    def from_string(cls, s):
        match = re.match('([A-Za-z]+):\s*([^\[]+)\[([^\]]+)\]$', s)
        if not match:
            raise ValueError(s)
        return cls(*match.groups())


@attr.s
class RelatedSocieties(object):
    id = attr.ib()
    related = attr.ib(convert=lambda s: [
        RelatedSociety.from_string(ss) for ss in semicolon_split(s)])


@attr.s
class Dataset(ObjectWithSource):
    type = attr.ib(validator=partial(valid_enum_member, ['cultural', 'environmental']))
    description = attr.ib()

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
    def society_relations(self):
        return [
            RelatedSocieties(**d) for d in self._items('societies_mapping', dicts=True)]

    @property
    def variables(self):
        codes = {vid: list(c) for vid, c in groupby(
            sorted(self._items('codes', namedtuples=True), key=lambda c: c.var_id),
            lambda c: c.var_id)}
        return [
            Variable(codes=codes.get(v['id'], []), **v)
            for v in self._items('variables', dicts=True)]


@attr.s
class Phylogeny(ObjectWithSource):
    scaling = attr.ib()

    @property
    def trees(self):
        return self.dir.joinpath('summary.trees')

    @property
    def taxa(self):
        return list(reader(self.dir.joinpath('taxa.csv'), dicts=True))


class Repos(object):
    def __init__(self, dir_):
        self.dir = dir_
        self.datasets = [
            Dataset(base_dir=self.dir.joinpath('datasets'), **r) for r in
            reader(self.dir.joinpath('datasets', 'index.csv'), dicts=True)]
        self.phylogenies = [
            Phylogeny(base_dir=self.dir.joinpath('phylogenies'), **r) for r in
            reader(self.dir.joinpath('phylogenies', 'index.csv'), dicts=True)]

    def path(self, *comps):
        return self.dir.joinpath(*comps)

    def read_csv(self, *comps, **kw):
        return list(reader(self.path(*comps), **kw))

    def read_json(self, *comps):
        return jsonlib.load(self.path(*comps))


def load(repos, test=True):
    configure_logging(test=test)
    repos = Repos(repos)

    for func in [
        load_societies,
        load_society_relations,
        load_regions,
        society_locations,
        load_vars,
        load_languages,
        load_references,
        load_data,
        load_phylogenies,
    ]:
        with transaction.atomic():
            if not test:
                print("%s..." % func.__name__)  # pragma: no cover
            start = time()
            res = func(repos)
            if not test:  # pragma: no cover
                print("{0} loaded in {1:.2f} secs".format(res, time() - start))


if __name__ == '__main__':  # pragma: no cover
    load(Path(sys.argv[1]), test=False)
    sys.exit(0)
