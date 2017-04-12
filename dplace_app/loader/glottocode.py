# -*- coding: utf-8 -*-
import logging

from dplace_app.models import Language, LanguageFamily, Society


def load_languages(repos):
    languoids = {
        l.id: l for l in repos.read_csv('csv', 'glottolog.csv', namedtuples=True)}
    families, languages = {}, {}
    societies = {s.ext_id: s for s in Society.objects.all()}
    for ds in repos.datasets:
        for soc in ds.societies:
            ldata = languoids.get(soc.glottocode)
            if not ldata:  # pragma: no cover
                logging.warning("No language found for %s, skipping" % soc.glottocode)
                continue

            soc = societies[soc.id]
            soc.language = load_language(ldata, languages, families)
            soc.save()
    return len(languages)


def load_language(ldata, languages, families):
    # get or create the language family:
    # Note: If the related languoid is an isolate or a top-level family, we create a
    # LanguageFamily object with the data of the languoid.
    family_id = ldata.family_id or ldata.id
    family = families.get(family_id)
    if not family:
        family_name = ldata.family_name or ldata.name
        family = LanguageFamily.objects.create(name=family_name)
        family.save()
        families[family_id] = family

    # get or create the language:
    language = languages.get(ldata.id)
    if not language:
        language = Language.objects.create(
            name=ldata.name, glotto_code=ldata.id, iso_code=ldata.iso_code)
        language.family = family
        language.save()
        languages[ldata.id] = language
    return language
