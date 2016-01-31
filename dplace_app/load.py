# -*- coding: utf-8 -*-
import sys
from itertools import chain

import django
from django.db import transaction

from load.util import configure_logging, csv_dict_reader, stream
from load.isocode import load_isocode
from load.environmental import load_environmental
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
    'soc_lat_long': society_locations,
    'ea_soc': load_ea_society,
    'bf_soc': load_bf_society,
    'vars': load_vars,
    'glotto_iso': map_isocodes,
    'xd_lang': xd_to_language,
}


def run(mode, *fnames):
    configure_logging()
    file_name = fnames[0]

    if mode == 'geo':
        load_regions(file_name)
    elif mode == 'tree':
        load_tree(file_name)
    else:
        row_loader = LOAD_BY_ROW.get(mode)
        if row_loader:
            for dict_row in csv_dict_reader(file_name):
                row_loader(dict_row)
        elif mode == 'vals':
            # coded values can only be created al at once now, so we must make sure to
            # pass in all csv files with values.
            load_data(chain(*map(csv_dict_reader, fnames)))
        elif mode == 'glotto':
            load_glottocode(csv_dict_reader(file_name))
        elif mode == 'refs':
            load_references(file_name)
        elif mode == 'codes':
            load_codes(stream(file_name))
        elif mode == 'env_vals':
            load_environmental(csv_dict_reader(file_name))
        else:
            raise ValueError(mode)

        if mode == 'xd_lang':
            update_language_counts()

    if len(MISSING_CODES) > 0:
        print "Missing ISO Codes:"
        print '\n'.join(MISSING_CODES)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "\nUsage: %s source_file mode" % sys.argv[0]
        print "You should run load_all_datasets.sh instead of this script directly."
        print
        sys.exit(1)
    django.setup()
    with transaction.atomic():
        run(sys.argv[-1], *[arg.strip() for arg in sys.argv[1:-1]])
    sys.exit(0)
