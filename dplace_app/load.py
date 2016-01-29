# -*- coding: utf-8 -*-
import sys

import django
from django.db import transaction

from load.util import configure_logging, csv_dict_reader, stream
from load.isocode import load_isocode
from load.environmental import load_environmental, create_environmental_variables
from load.language import update_language_counts, MISSING_CODES
from load.society_ea import load_ea_society, society_locations
from load.society_binford import load_bf_society
from load.geographic import load_regions
from load.tree import load_tree
from load.variables import load_vars, load_codes
from load.values import load_data
from load.sources import load_references
from load.glottocode import load_glottocode, map_isocodes, xd_to_language


LOAD_BY_ROW = {
    'iso': load_isocode,
    'env_vals': load_environmental,
    #'langs': ,
    'soc_lat_long': society_locations,
    'ea_soc': load_ea_society,
    'bf_soc': load_bf_society,
    'bf_vals': load_data,
    'vars': load_vars,
    'ea_vals': load_data,
    'glotto_iso': map_isocodes,
    'xd_lang': xd_to_language,
    #'ea_refs': ,
}


def run(file_name, mode):
    configure_logging()

    if mode == 'geo':
        load_regions(file_name)
    elif mode == 'tree':
        load_tree(file_name)
    elif mode == 'glottotree':
        load_tree(file_name)
    else:
        row_loader = LOAD_BY_ROW.get(mode)
        if row_loader:
            for dict_row in csv_dict_reader(file_name):
                row_loader(dict_row)
        elif mode == 'glotto':
            load_glottocode(csv_dict_reader(file_name))
        elif mode == 'refs':
            load_references(file_name)
        elif mode == 'codes':
            load_codes(stream(file_name))
        elif mode == 'env_vars':
            create_environmental_variables()
        elif mode == 'langs' or mode == 'xd_lang':
            update_language_counts()
        else:
            raise ValueError(mode)

    if len(MISSING_CODES) > 0:
        print "Missing ISO Codes:"
        print '\n'.join(MISSING_CODES)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "\nUsage: %s source_file mode" % sys.argv[0]
        print "You should run load_all_datasets.sh instead of this script directly."
        print
        sys.exit(1)
    django.setup()
    with transaction.atomic():
        run(sys.argv[1], sys.argv[2].strip())
    sys.exit(0)
