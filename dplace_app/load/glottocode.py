# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from dplace_app.models import Language, ISOCode, Society, LanguageFamily

from util import delete_all


def xd_to_language(items, languoids):
    delete_all(Language)
    delete_all(LanguageFamily)
    delete_all(ISOCode)

    glottolog = {l['id']: l for l in languoids}

    societies_ = defaultdict(list)
    for s in Society.objects.all():
        societies_[s.xd_id].append(s)
    families = {}
    languages = {}
    isocodes = {}

    count = 0
    for item in items:
        societies = societies_.get(item['xd_id'])
        if not societies:  # pragma: no cover
            logging.warning("No societies found with xd_id %(xd_id)s" % item)
            continue

        ldata = glottolog.get(item['DialectLanguageGlottocode'])
        if not ldata:  # pragma: no cover
            logging.warning("No language found for %s, skipping" % item)
            continue

        _xd_to_language(item, societies, ldata, languages, families, isocodes)
        count += 1
    return count


def _xd_to_language(dict_row, societies, ldata, languages, families, isocodes):
    # get or create the language family:
    # Note: If the related languoid is an isolate or a top-level family, we create a
    # LanguageFamily object with the data of the languoid.
    family_id = ldata['family_id'] or ldata['id']
    family = families.get(family_id)
    if not family:
        family_name = ldata['family_name'] or ldata['name']
        family = LanguageFamily.objects.create(name=family_name, scheme='G')
        family.save()
        families[family_id] = family

    # get or create the language:
    language = languages.get(ldata['id'])
    if not language:
        language = Language.objects.create(name=ldata['name'], glotto_code=ldata['id'])
        language.family = family

        if ldata['iso_code']:
            if len(ldata['iso_code']) > 3:  # pragma: no cover
                logging.warning("ISOCode too long, skipping %s" % ldata['iso_code'])
            else:
                isocode = isocodes.get(ldata['iso_code'])
                if not isocode:
                    isocode = ISOCode.objects.create(iso_code=ldata['iso_code'])
                    isocodes[ldata['iso_code']] = isocode
                language.iso_code = isocode

        language.save()
        languages[ldata['id']] = language

    for soc in societies:
        soc.language = language
        soc.save()
