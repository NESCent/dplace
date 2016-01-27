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
    xd_id = dict_row['xd_id'].strip()
    isocode = dict_row['iso_6933'].strip()
    glottocode = dict_row['DialectLanguageGlottocode'].strip()
    family_glottocode = dict_row['FamilyGlottocode'].strip()
    
    iso, created = ISOCode.objects.get_or_create(iso_code=isocode)
    glotto, created = GlottoCode.objects.get_or_create(glotto_code=glottocode)
    family, created = GlottoCode.objects.get_or_create(glotto_code=family_glottocode)
    
    societies = Society.objects.all().filter(xd_id=xd_id)
    if len(societies) == 0:
        print "No societies found with xd_id %s" % (xd_id)
        return
    else:
        #get or create language family
        try:
            family_language = Language.objects.get(glotto_code=family)
            lang_fam, created = LanguageFamily.objects.get_or_create(scheme='G', name=family_language.name)
            if created:
                print "Language Family %s created" % (lang_fam.name)
        except ObjectDoesNotExist:
            print "No language found for family glottocode %s, skipping" % family_glottocode
            lang_fam = None
            
        try:
            language = Language.objects.get(iso_code=iso, glotto_code=glotto)
            if lang_fam:
                language.family = lang_fam
                language.save()
            for s in societies:
                s.language = language
                s.save()
        except ObjectDoesNotExist:
            try:
                language = Language.objects.get(glotto_code=glotto)
                if lang_fam:
                    language.family = lang_fam
                    language.save()
                for s in societies:
                    s.language = language
                    s.save()
            except ObjectDoesNotExist:
                print "No language found for isocode %s and glottocode %s, skipping" % (isocode, glottocode)
                return        
