# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *
from isocode import get_isocode, get_value
from environmental import iso_from_code

MISSING_CODES = []
def add_missing_isocode(isocode):
    MISSING_CODES.append(isocode)

def load_lang(lang_row):
    # Extract values from dictionary
    code = get_isocode(lang_row)
    if code is None:
        logging.warn("No ISO Code found, skipping")
        return None
    language_name = get_value(lang_row,('Language name','NAM'))
    #ethnologue_classification = get_value(lang_row,('Ethnologue Classification (unrevised)','Ethnologue classification (if applicable)'))
    family_names = [
        get_value(lang_row,('FAMILY-REVISED','FAMILY')),
        lang_row['Class2'],
        lang_row['Class3']
    ]
    # ISO Code
    isocode = iso_from_code(code) # Does not create new ISO Codes
    if isocode is None:
        logging.warn(
            "No ISO Code found in database for %s, skipping language %s" % (code, language_name)
        )
        add_missing_isocode(code)
        return None

    # Language
    try:
        language = Language.objects.get(iso_code=isocode)
    except ObjectDoesNotExist:
        language = Language(name=language_name, iso_code=isocode)
        language.save()
        logging.info("Created Language: %s" % language_name)
    
    # Classes
    classes = []
    for i in range(3):
        level = i + 1
        name = family_names[i].strip()
        if len(name) == 0:
            # empty cell
            continue
        try:
            classes.append(LanguageClass.objects.get(scheme='R',level=level,name=name))
        except ObjectDoesNotExist:
            if len(classes) > 0:
                parent = classes[-1]
            else:
                parent = None
            lang_class = LanguageClass(scheme='R',level=level, name=name, parent=parent)
            lang_class.save()
            logging.info("Created Language Class: %s" % name)
            classes.append(lang_class)

    # Finally, create the LanguageClassification
    classification_scheme = 'R' # Ethnologue17-Revised
    class_family = classes[0]
    class_subfamily = classes[1] if len(classes) > 1 else None
    class_subsubfamily = classes[2] if len(classes) > 2 else None
    classification = LanguageClassification.objects.get_or_create(
        scheme=classification_scheme,
        language=language,
        class_family=class_family,
        class_subfamily=class_subfamily,
        class_subsubfamily=class_subsubfamily
    )
    logging.info('Created Classification')
    return language

def update_language_counts():
    for language_class in LanguageClass.objects.all():
        language_class.update_counts()
