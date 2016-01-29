# -*- coding: utf-8 -*-
from dplace_app.models import LanguageFamily

MISSING_CODES = []


def add_missing_isocode(isocode):
    MISSING_CODES.append(isocode)


def update_language_counts():
    print "Updating language counts"
    for language_family in LanguageFamily.objects.all():
        language_family.update_counts()
