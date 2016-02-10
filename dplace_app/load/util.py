# coding: utf8
from __future__ import unicode_literals
import csv
import logging

from six import BytesIO
from django.db import connection

def delete_all(model):
    model.objects.all().delete()
    with connection.cursor() as c:
        c.execute(
            "ALTER SEQUENCE %s_id_seq RESTART WITH 1" % model._meta.db_table
        )


def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)


def bfvar_number_to_label(number):
    return "B{0:0>3}".format(number)


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


def stream(fname):
    with open(fname, 'rb') as fp:
        stream_ = BytesIO(
            fp.read().replace(b'\x90', b'').replace(b'\x8b', b' ')
        )
        stream_.seek(0)
        return stream_


def csv_reader(fname):
    for row in csv.reader(stream(fname)):
        yield [
            col if col is None else col.decode('utf8').strip() for col in row
        ]


def csv_dict_reader(fname):
    for dict_row in csv.DictReader(stream(fname)):
        for k in dict_row:
            if dict_row[k] is None:
                continue
            try:
                dict_row[k] = dict_row[k].decode('utf8').strip()
            except:
                logging.warn('cannot decode row item %s in %s' % (k, dict_row))
        yield dict_row
