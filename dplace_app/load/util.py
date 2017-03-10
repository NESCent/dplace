# coding: utf8
from __future__ import unicode_literals
import logging

from clldutils.dsv import reader


def configure_logging(test=False):
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL if test else logging.INFO)
    # file load.log gets everything
    fh = logging.FileHandler('load.log')
    fh.setLevel(logging.CRITICAL if test else logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL if test else logging.WARN)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s:%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def csv_dict_reader(fname):
    return reader(fname, dicts=True)
