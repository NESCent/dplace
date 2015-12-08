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
    classification_scheme = 'G' #Glottolog
    xd_id = dict_row['xd_id']
    glottocode = dict_row['DialectLanguageGlottocode']
    family_glottocode = dict_row['FamilyGlottocode']
    
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glottocode)
    family, created = GlottoCode.objects.get_or_create(glotto_code=family_glottocode)
    
    societies = Society.objects.all().filter(xd_id=xd_id)
    if len(societies) == 0:
        print "No societies found with xd_id %s" % (xd_id)
    else:
        for s in societies:
            s.glotto_code = glotto
            s.save()

    try:
        language = Language.objects.get(glotto_code=glotto)
    except ObjectDoesNotExist:
        print "No language found for glottocode %s, skipping" % glottocode
        return
    try:
        family_language = Language.objects.get(glotto_code=family)
    except ObjectDoesNotExist:
        print "No language found for family glottocode %s, skipping" % family_glottocode
        return
        
    class_level = 1
    lang_class, created = LanguageClass.objects.get_or_create(scheme=classification_scheme, level=class_level, name=family_language.name)
    if created:
        print "Created language class for famimly %s" % family_language.name
    lang_class.save()
    classification, created = LanguageClassification.objects.get_or_create(
                                                            scheme=classification_scheme,
                                                            language=language,
                                                            class_family=lang_class,
                                                            )
    classification.save()
    if created:
        print "Saved classification %s, %s" % (xd_id, glotto)
                                                            
                                                            