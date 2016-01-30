# -*- coding: utf-8 -*-
import logging
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *
from isocode import get_isocode, get_value
from environmental import iso_from_code

MISSING_CODES = []
def add_missing_isocode(isocode):
    MISSING_CODES.append(isocode)

def update_language_counts():
    print "Updating language counts"
    for language_family in LanguageFamily.objects.all():
        language_family.update_counts()
