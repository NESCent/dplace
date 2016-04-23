# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from dplace_app.models import ISOCode, Society, Language, LanguageFamily
from dplace_app.models import Environmental, EnvironmentalCategory
from dplace_app.models import EnvironmentalVariable, EnvironmentalValue
from sources import get_source

_ISO_CODES = None


def iso_from_code(code):
    global _ISO_CODES
    if _ISO_CODES is None:
        _ISO_CODES = {c.iso_code: c for c in ISOCode.objects.all()}
    return _ISO_CODES.get(code)


def clean_category(category):
    return category.strip().capitalize()


def load_environmental_var(items):
    categories = {}

    count = 0
    for item in items:
        if load_env_var(item, categories):
            count += 1
    return count


def load_env_var(var_dict, categories):
    if var_dict['VarType'].strip() != 'Continuous':
        return False
    index_category = None
    for c in map(clean_category, var_dict['IndexCategory'].split(',')):
        index_category = categories.get(c)
        if not index_category:
            index_category = categories[c] = EnvironmentalCategory.objects.create(name=c)
            logging.info("Created EnvironmentalCategory: %s" % c)
    
    variable, created = EnvironmentalVariable.objects.get_or_create(
        var_id=var_dict['VarID'],
        name=var_dict['Name'],
        units=var_dict['Units'],
        category=index_category,
        codebook_info=var_dict['Description']
    )
    if created:
        logging.info("Saved environmental variable %s" % variable)
    return True


def load_environmental(items):
    variables = {v.var_id: v for v in EnvironmentalVariable.objects.all()}
    societies = {(s.ext_id, s.source_id): s for s in Society.objects.all()}
    res = 0
    objs = []
    for item in items:
        if item['Dataset'] in ['EA', 'Binford']:
            if _load_environmental(item, variables, societies, objs):
                res += 1
    EnvironmentalValue.objects.bulk_create(objs, batch_size=1000)
    for language_family in LanguageFamily.objects.all():
        language_family.update_counts()
    return res


_missing_variables = set()


def _load_environmental(val_row, variables, societies, objs):
    global _missing_variables
    ext_id = val_row['soc_id']
    source = get_source(val_row['Dataset'])

    # hack for B109 vs. 109
    if source.author == 'Binford' and ext_id.find('B') == -1:
        ext_id = 'B' + ext_id

    society = societies.get((ext_id, source.id))
    if society is None:
        logging.warn(
            "Unable to find a Society object with ext_id %s and source %s, skipping..." %
            (ext_id, source))
        return
    
    # This limits the environmental data to one record per society record
    found_environmentals = Environmental.objects.filter(society=society).all()
    if len(found_environmentals) == 0:
        if society.language is not None:
            iso_code = society.language.iso_code
        else:
            iso_code = None
        # Create the base Environmental
        environmental, created = Environmental.objects.get_or_create(
            society=society,
            source=source,
            iso_code=iso_code
        )
    else:
        environmental = found_environmentals[0]
        
    variable = variables.get(val_row['variable'])
    if variable is None:
        if val_row['variable'] not in _missing_variables:
            logging.warn("Could not find environmental variable %s" % val_row['variable'])
            _missing_variables.add(val_row['variable'])
        return

    objs.append(EnvironmentalValue(
        variable=variable,
        value=float(val_row['value']),
        comment=val_row['comment'],
        environmental=environmental,
        source=source
    ))
    return True
