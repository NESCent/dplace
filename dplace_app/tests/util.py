# coding: utf8
from __future__ import unicode_literals, print_function, division
import os


def data_path(fname=None):
    comps = ['data']
    if fname is not None:
        comps.append(fname)
    return os.path.join(os.path.dirname(__file__), *comps)
