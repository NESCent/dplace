# coding: utf8
from __future__ import unicode_literals
import csv
import logging

from six import BytesIO

from dplace_app.models import Society


def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)


def bfvar_number_to_label(number):
    return "B{0:0>3}".format(number)


def load_society(society_dict, source):
    society, created = Society.objects.get_or_create(ext_id=society_dict['soc_id'])
    society.xd_id = society_dict['xd_id']
    society.name = society_dict['soc_name']
    society.source = source
    society.alternate_names = society_dict['alternate_names']
    society.focal_year = society_dict['main_focal_year']

    logging.info("Saving society %s" % society)
    society.save()
    return society


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # file load.log gets everything
    fh = logging.FileHandler('load.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARN)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s:%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def stream(fname):
    with open(fname, 'rb') as fp:
        stream_ = BytesIO(fp.read().replace(b'\x90', b'').replace(b'\x8b', b' '))
        stream_.seek(0)
        return stream_


def csv_reader(fname):
    for row in csv.reader(stream(fname)):
        yield [col if col is None else col.decode('utf8').strip() for col in row]


def csv_dict_reader(fname):
    for dict_row in csv.DictReader(stream(fname)):
        for k in dict_row:
            if dict_row[k] is None:
                continue
            dict_row[k] = dict_row[k].decode('utf8').strip()
        yield dict_row
