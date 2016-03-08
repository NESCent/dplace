#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import chain
from time import time

import django
django.setup()

from django.db import transaction

from load.util import configure_logging, csv_dict_reader
from load.society import society_locations, load_societies
from load.environmental import load_environmental, load_environmental_var
from load.geographic import load_regions
from load.tree import load_trees
from load.variables import load_vars, load_codes
from load.values import load_data
from load.sources import load_references
from load.glottocode import xd_to_language


ITEM_LOADER = dict(
    soc_lat_long=society_locations,
    soc=load_societies,
    vars=load_vars,
    vals=load_data,
    codes=load_codes,
    env_vals=load_environmental,
    env_vars=load_environmental_var,
    refs=load_references,
)


def run(mode, *fnames):  # pragma: no cover
    configure_logging()

    if mode == 'geo':
        return load_regions(fnames[0])
    if mode == 'tree':
        return load_trees(fnames[0])
    if mode == 'xd_lang':
        return xd_to_language(csv_dict_reader(fnames[0]), csv_dict_reader(fnames[1]))
    if mode in ITEM_LOADER:
        return ITEM_LOADER[mode](chain(*map(csv_dict_reader, fnames)))
    raise ValueError(mode)


if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv) < 3:
        print "\nUsage: %s source_file mode" % sys.argv[0]
        print "You should run load_all_datasets.sh instead of this script directly."
        print
        sys.exit(1)
    django.setup()
    with transaction.atomic():
        print sys.argv[-1], '...'
        start = time()
        res = run(sys.argv[-1], *[arg.strip() for arg in sys.argv[1:-1]])
        print res, 'loaded in', time() - start, 'secs'
    sys.exit(0)
