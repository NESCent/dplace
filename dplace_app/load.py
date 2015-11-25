# -*- coding: utf-8 -*-
import csv
import sys
from django.db import transaction
from load.isocode import *
from load.environmental import *
from load.language import *
from load.society_ea import *
from load.society_binford import *
from load.geographic import *
from load.tree import *
from load.variables import *
from load.values import *
from load.sources import *
from load.glottocode import *

#iso = load isocodes
#env_vals = load environmental values
#langs =
#soc_lat_long = load locations for societies
#ea_soc = load EA societies
#bf_soc = 
#bf_vals = 
#vars = load (EA or BF) variables
#ea_stacked = load EA stacked

LOAD_BY_ROW=('iso', 'env_vals',
             'langs','soc_lat_long',
             'ea_soc','bf_soc', 'bf_vals',
             'vars', 'ea_vals', 'glotto',
             'xd_lang', 'ea_refs')

def run(file_name=None, mode=None):
    if mode == 'geo':
        load_regions(file_name)
    elif mode == 'tree':
        load_tree(file_name)
    elif mode == 'glottotree':
        load_glotto_tree(file_name)
    else:
        # read the csv file
        with open(file_name, 'rb') as csvfile:
            if mode in LOAD_BY_ROW:
                csv_reader = csv.DictReader(csvfile)
                for dict_row in csv_reader:
                    if mode == 'iso':
                        load_isocode(dict_row)
                    elif mode == 'vars':
                        load_vars(dict_row)
                    elif mode == 'ea_soc':
                        load_ea_society(dict_row)
                    elif mode == 'soc_lat_long':
                        society_locations(dict_row)
                    elif mode == 'env_vals':
                        load_environmental(dict_row)
                    elif mode == 'ea_vals':
                        load_data(dict_row)
                    elif mode == 'bf_vals':
                        load_data(dict_row)
                    elif mode == 'ea_refs':
                        load_val_references(dict_row)
                    elif mode == 'langs':
                        load_lang(dict_row)
                    elif mode == 'bf_soc':
                        load_bf_society(dict_row)
                    elif mode == 'glotto':
                        load_glottocode(dict_row)
                    elif mode == 'xd_lang':
                        xd_to_language(dict_row)
            elif mode == 'refs': #load references
                load_references(csvfile)
            elif mode == 'codes': #load codes for variables
                load_codes(csvfile)
        if len(MISSING_CODES) > 0:
            print "Missing ISO Codes:"
            print '\n'.join(MISSING_CODES)
        elif mode == 'env_vars':
            create_environmental_variables()
        elif mode == 'langs' or mode == 'xd_lang':
            update_language_counts()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "\nUsage: %s source_file mode" % sys.argv[0]
        print "You should run load_all_datasets.sh instead of this script directly."
        print
    else:
        try:
            transaction.enter_transaction_management()
            transaction.managed(True)
            run(sys.argv[1], sys.argv[2])
        finally:
            transaction.commit()
            