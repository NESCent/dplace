# -*- coding: utf-8 -*-
from sources import get_source

from util import load_society


def load_bf_society(society_dict):
    return load_society(society_dict, get_source('Binford'))
