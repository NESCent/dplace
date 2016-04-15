#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from itertools import chain
from time import time
import os
from functools import partial

import django
django.setup()

from django.db import transaction

from load.util import configure_logging, csv_dict_reader
from load.society import society_locations, load_societies
from load.environmental import load_environmental, load_environmental_var
from load.geographic import load_regions
from load.tree import load_trees, tree_names, prune_trees
from load.variables import load_vars, load_codes
from load.values import load_data
from load.sources import load_references
from load.glottocode import xd_to_language


def data_path(category, *comps):
    return os.path.join(os.path.dirname(__file__), '..', 'datasets', category, *comps)

csv_path = partial(data_path, 'csv')


def csv_items(*names):
    return chain(*[csv_dict_reader(csv_path(name)) for name in names])


def main():  # pragma: no cover
    configure_logging()

    for spec in [
        # Loading Societies
        (
            load_societies,
            csv_items(
                'EA_header_data_24Feb2016.csv', 'Binford_header_data_24Feb2016.csv')),
        # Loading Geographic regions
        (load_regions, data_path('geo', 'level2.json')),
        # Linking Societies to Locations
        (society_locations, csv_items('society_locations.csv')),
        # Loading Variables
        (load_vars, csv_items('EAVariableList.csv', 'BinfordVariableList.csv')),
        # Loading Variable Codes
        (
            load_codes,
            csv_items('EACodeDescriptions.csv', 'BinfordCodeDescriptions.csv')),
        # Linking Societies to Languoids
        (
            xd_to_language,
            csv_items('xd_id_to_language.csv'), csv_items('glottolog.csv')),
        # Loading References
        (
            load_references,
            csv_items('ReferenceMapping.csv', 'BinfordReferenceMapping.csv')),
        # Loading Data
        (load_data, csv_items('EA_DATA_Stacked.csv', 'Binford_DATA_stacked.csv')),
        # Loading Environmental Data
        (load_environmental_var, csv_items('EnvironmentalVariables.csv')),
        (load_environmental, csv_items('EnvData.csv')),
        # Loading Trees
        (load_trees, data_path('trees')),
        (tree_names, data_path('csv')),
        (prune_trees,),
    ]:
        with transaction.atomic():
            loader, args = spec[0], spec[1:]
            print loader.__name__, '...'
            start = time()
            res = loader(*args)
            print res, 'loaded in', time() - start, 'secs'


if __name__ == '__main__':  # pragma: no cover
    main()
    sys.exit(0)
