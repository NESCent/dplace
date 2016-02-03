# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

from dplace_app.models import Language, ISOCode, Society, LanguageFamily

from util import delete_all


def load_languages(items):
    delete_all(Language)
    Language.objects.bulk_create(
        [Language(name=i['name'], glotto_code=i['id']) for i in items], batch_size=1000)
    return Language.objects.count()


def map_isocodes(items):
    """
    Matches isocodes to glottocodes.
    """
    languages = {l.glotto_code: l for l in Language.objects.all()}

    count = 0
    for dict_row in items:
        glotto_code = dict_row['id']
        iso_code = dict_row['iso_code']
        if not iso_code:
            continue

        if len(iso_code) > 3:
            logging.warning("ISOCode too long, skipping %s" % iso_code)
            continue
        
        iso, created = ISOCode.objects.get_or_create(iso_code=iso_code)
        language = languages.get(glotto_code)
        if language:
            language.iso_code = iso
            language.save()
            logging.info("Mapped isocode %s to glottocode %s" % (iso_code, glotto_code))
            count += 1
        else:
            logging.warning("No language found with glottocode %s" % glotto_code)
    return count


def xd_to_language(items):
    languages = {l.glotto_code: l for l in Language.objects.all()}
    societies = defaultdict(list)
    for s in Society.objects.all():
        societies[s.xd_id].append(s)
    families = {}

    count = 0
    for item in items:
        if _xd_to_language(item, languages, societies, families):
            count += 1
    for language_family in LanguageFamily.objects.all():
        language_family.update_counts()
    return count


def _xd_to_language(dict_row, languages, societies, families):
    glottocode = dict_row['DialectLanguageGlottocode']
    family_glottocode = dict_row['FamilyGlottocode']

    societies = societies.get(dict_row['xd_id'])
    if not societies:
        logging.warning("No societies found with xd_id %(xd_id)s" % dict_row)
        return False

    # get or create language family
    family_language = languages.get(family_glottocode)
    if family_language:
        lang_fam = families.get(family_language.name)
        if not lang_fam:
            lang_fam = families[family_language.name] = LanguageFamily.objects.create(
                scheme='G', name=family_language.name)
            logging.info("Language Family %s created" % (lang_fam.name))
    else:
        logging.warning("No language found for family glottocode %s, skipping"
                        % family_glottocode)
        lang_fam = None

    language = languages.get(glottocode)
    if language:
        if lang_fam and not language.family:
            language.family = lang_fam
            language.save()
        for s in societies:
            s.language = language
            s.save()
        return True
    logging.warning("No language found for glottocode %s, skipping" % glottocode)
    return False
