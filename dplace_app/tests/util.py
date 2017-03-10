# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.path import Path


def data_path(*comps):
    return Path(__file__).parent.joinpath('data', *comps)
