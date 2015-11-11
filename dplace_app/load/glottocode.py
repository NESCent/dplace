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
    name = dict_row['name']
   # level = dict_row['level']
   # parent_id = dict_row['parent_id']
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glotto_code)
    
    if not iso_code:
        language, created = Language.objects.get_or_create(name=name, glotto_code=glotto)
        if created:
            print "Created language %s, glottocode %s" % (name, glotto)
        language.save()
    else:
        try:
            language = Language.objects.get(iso_code__iso_code=iso_code)
            if glotto:
                language.glotto_code = glotto
                language.save()
        except ObjectDoesNotExist:
            print "No language found for ISO Code %s" % iso_code
            return
            
def xd_to_language(dict_row):
    """
    Reads file xd_id_to_language.csv
    """
    
    xd_id = dict_row['xd_id']
    glottocode = dict_row['glottocode']
    
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glottocode)
    
    try:
        society = Society.objects.get(xd_id=xd_id)
        society.glotto_code = glotto
        society.save()
    except:
        print "No society found for xd_id %s glottocode %s" % (xd_id, glottocode)