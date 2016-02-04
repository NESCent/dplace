# -*- coding: utf-8 -*-
import logging
from dplace_app.models import ISOCode

ISOCODE_UPDATE = {}
ISOCODE_UPDATE['mld'] = 'oru'
ISOCODE_UPDATE['ggr'] = 'gtu'
ISOCODE_UPDATE['djl'] = 'dze'
ISOCODE_UPDATE['gbc'] = 'wrk'
ISOCODE_UPDATE['mnt'] = 'xyk'
ISOCODE_UPDATE['mwd'] = 'dmw'
ISOCODE_UPDATE['nbx'] = 'ekc'
ISOCODE_UPDATE['baz'] = 'tvu'
ISOCODE_UPDATE['noo'] = 'nuk'
ISOCODE_UPDATE['gio'] = 'giq'  # or gir, giw
ISOCODE_UPDATE['nbf'] = 'nxq'
ISOCODE_UPDATE['tkk'] = 'twm'
ISOCODE_UPDATE['daf'] = 'dnj'
ISOCODE_UPDATE['acc'] = 'acr'
ISOCODE_UPDATE['ixi'] = 'ixl'
ISOCODE_UPDATE['lcq'] = 'ppr'  # ppr in version 17, back to lcq in 18. Whee!
ISOCODE_UPDATE['bjq'] = 'bzc'
ISOCODE_UPDATE['kdv'] = 'zkd'
ISOCODE_UPDATE['kpp'] = 'jkp'
ISOCODE_UPDATE['agp'] = 'prf'
ISOCODE_UPDATE['sul'] = 'sgd'
ISOCODE_UPDATE['stc'] = 'ntu'
ISOCODE_UPDATE['rmr'] = 'rmq'
ISOCODE_UPDATE['wit'] = 'wnw'
ISOCODE_UPDATE['vlr'] = 'vra'
ISOCODE_UPDATE['unp'] = 'wro'
ISOCODE_UPDATE['wiw'] = 'wgu'
ISOCODE_UPDATE['yen'] = 'ynq'
ISOCODE_UPDATE['wgw'] = 'wgb'

ISOCODE_IGNORE = [
    'mja',  # Spurious
    'aay',  # Spurious
    'pie',  # Extinct
]


def get_value(dict, *possible_keys):
    '''
    Get a value from a dictionary, searching the possible keys in order
    '''
    for key in possible_keys:
        if key in dict:
            return dict[key]


def get_isocode(dict):
    '''
    ISO Code may appear in 'ISO' column (17th Ed Missing ISO codes)
    or the 'ISO 693-3 code' column (17th Ed - ISO 693-3 - current)
    '''
    return get_value(dict, 'ISO', 'ISO 693-3 code', 'ISO693_3')


def load_isocode(iso_dict):
    code = get_isocode(iso_dict)
    if code is None:
        logging.warn("ISO Code not found in row, skipping")
        return
    if len(code) > 3:
        logging.warn("ISO Code '%s' too long, skipping" % code)
        return
    return ISOCode.objects.get_or_create(iso_code=code)
