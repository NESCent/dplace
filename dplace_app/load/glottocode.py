# -*- coding: utf-8 -*-
# __author__ = 'dan'
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *

def load_glottocode(dict_row):
    """
    Reads file glottolog_mapping.csv
    """

    glotto_code = dict_row['id'].strip()
    name = dict_row['name'].strip()
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glotto_code)
    language, created = Language.objects.get_or_create(glotto_code=glotto)
    language.name = name
    language.save()
    print "Saved Glottocode %s, %s" % (name, glotto)

def map_isocodes(dict_row):
    """
    Matches isocodes to glottocodes.
    """

    glotto_code = dict_row['id'].strip()
    iso_code = dict_row['iso_693-3'].strip()
    if not iso_code:
        return
        
    if len(iso_code) > 3:
        print "ISOCode too long, skipping %s" % iso_code
        return
        
    iso, created = ISOCode.objects.get_or_create(iso_code=iso_code)
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glotto_code)
    
    try:
        language = Language.objects.get(glotto_code=glotto)
        language.iso_code = iso
        language.save()
        print "Mapped isocode %s to glottocode %s" % (iso_code, glotto_code)
    except ObjectDoesNotExist:
        print "No language found with glottocode %s" % glotto_code
    
    
def xd_to_language(dict_row):
    """
    Reads file xd_id_to_language.csv
    """
    
    classification_scheme = 'G' # for Glottolog
    xd_id = dict_row['xd_id']
    isocode = dict_row['iso_6933']
    glottocode = dict_row['DialectLanguageGlottocode']
    family_glottocode = dict_row['FamilyGlottocode']
    
    iso, created = ISOCode.objects.get_or_create(iso_code=isocode)
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glottocode)
    family, created = GlottoCode.objects.get_or_create(glotto_code=family_glottocode)
    
    societies = Society.objects.all().filter(xd_id=xd_id)
    if len(societies) == 0:
        print "No societies found with xd_id %s" % (xd_id)
    else:
        try:
            language = Language.objects.get(iso_code=iso, glotto_code=glotto)
            for s in societies:
                s.language = language
                s.save()
        except ObjectDoesNotExist:
            try:
                language = Language.objects.get(glotto_code=glotto)
                language.iso_code = iso
                language.save()
                print "Mapped isocode %s to glottocode %s" % (isocode, glottocode)
                for s in societies:
                    s.language = language
                    s.save()
            except ObjectDoesNotExist:
                print "No language found for isocode %s and glottocode %s, skipping" % (isocode, glottocode)

            return
            
    try:
        language = Language.objects.get(glotto_code=glotto, iso_code=iso)
    except ObjectDoesNotExist:
        print "No language found for glottocode %s and isocode %s, skipping" % (glottocode, isocode)
        return
    try:
        family_language = Language.objects.get(glotto_code=family)
    except ObjectDoesNotExist:
        print "No language found for family glottocode %s, skipping" % family_glottocode
        return
        
    class_level = 1
    lang_class, created = LanguageClass.objects.get_or_create(scheme=classification_scheme, level=class_level, name=family_language.name)
    if created:
        print "Created language class for family %s" % family_language.name.encode("UTF-8", "ignore")
    lang_class.save()
    classification, created = LanguageClassification.objects.get_or_create(
                                                            scheme=classification_scheme,
                                                            language=language,
                                                            class_family=lang_class,
                                                            )
    classification.save()
    if created:
        print "Saved classification %s, %s" % (xd_id, glotto)
                                                            
                                                            