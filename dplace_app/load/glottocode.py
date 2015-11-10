# -*- coding: utf-8 -*-
# __author__ = 'dan'
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *

def load_glottocode(dict_row):
    """
    Reads file glottolog_mapping.csv
    """
    iso_code = dict_row['iso_693-3']
    glotto_code = dict_row['id']
   # name = dict_row['name']
   # level = dict_row['level']
   # parent_id = dict_row['parent_id']
    try:
        language = Language.objects.get(iso_code__iso_code=iso_code)
        glotto, created = GlottoCode.objects.get_or_create(glotto_code=glotto_code)
        if glotto:
            language.glotto_code = glotto
            language.save()
    except ObjectDoesNotExist:
        return 