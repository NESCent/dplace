# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from dplace_app.models import ISOCode, Society
from dplace_app.models import Environmental, EnvironmentalCategory
from dplace_app.models import EnvironmentalVariable, EnvironmentalValue
from sources import get_source

ENVIRONMENTAL_MAP = {
    'AnnualMeanTemperature': {
        'name': 'Annual Mean Temperature',
        'category': 'Climate',
        'description': 'Mean value of monthly precipitation or temperature across the year',
        'units': '°C',
    },
    'AnnualTemperatureVariance': {
        'name': 'Annual Temperature Variance',
        'category': 'Climate',
        'description': 'Variance in temperature means (averaged across years)',
        'units': '°C',
    },
    'TemperatureConstancy': {
        'name': 'Temperature Constancy',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable because conditions are constant.',
    },
    'TemperatureContingency': {
        'name': 'Temperature Contingency',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable because conditions oscillate in a very predictable manner.',
    },
    'TemperaturePredictability': {
        'name': 'Temperature Predictability',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable due to either constancy or contingency.',
    },
    'AnnualMeanPrecipitation': {
        'name': 'Annual Mean Precipitation',
        'category': 'Climate',
        'units': 'mm',
        'description': 'Mean value of monthly precipitation.',
    },
    'AnnualPrecipitationVariance': {
        'name': 'Annual Precipitation Variance',
        'category': 'Climate',
        'units': '',
        'description': 'Variance in monthly precipitation means (averaged across years)',
    },
    'PrecipitationConstancy': {
        'name': 'Precipitation Constancy',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable because conditions are constant.',
    },
    'PrecipitationContingency': {
        'name': 'Precipitation Contingency',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable because conditions oscillate in a very predictable manner.',
    },
    'PrecipitationPredictability': {
        'name': 'Precipitation Predictability',
        'category': 'Climate',
        'units': '',
        'description': 'Colwell’s (1974) information theoretic index. Indicates the extent to which a climate patterns are predictable due to either constancy or contingency.'
    },
    'BirdRichness': {
        'name': 'Bird Richness',
        'category': 'Ecology',
        'units': '',
        'description': 'Number of coexisting species in a given taxonomic group.',
    },
    'MammalRichness': {
        'name': 'Mammal Richness',
        'category': 'Ecology',
        'units': '',
        'description': 'Number of coexisting species in a given taxonomic group.',
    },
    'AmphibianRichness': {
        'name': 'Amphibian Richness',
        'category': 'Ecology',
        'units': '',
        'description': 'Number of coexisting species in a given taxonomic group.',
    },
    'VascularPlantsRichness': {
        'name': 'Vascular Plants Richness',
        'category': 'Ecology',
        'units': '',
        'description': '',
    },
    # TODO: EcoRegion! (text)
    'Elevation': {
        'name': 'Elevation',
        'category': 'Physical landscape',
        'units': '',
        'description': 'Meters above sea level',
    },
    'Slope': {
        'name': 'Slope',
        'category': 'Physical landscape',
        'units': '',
        'description': 'Mean incline (in degrees) in the terrain (unit of sample 0.5 by 0.5 degree cell)',
    },
    # TODO: Coastal (Bool)
    'NetPrimaryProduction': {
        'name': 'Net Primary Production',
        'category': 'Ecology',
        'units': '',
        'description': 'grams of carbon taken in by plants per square meter of land per day',
    },
    'DurationOfGrowingSeason': {
        'name': 'Duration of Growing Season',
        'category': 'Climate',
        'units': 'mo',
        'description': 'Mean number of months in the year that net primary production is positive',
    },
    'MeanGrowingSeason.NPP': {
        'name': 'Mean Growing Season NPP',
        'category': 'Ecology',
        'units': '',
        'description': 'Mean net primary production during growing season',
    },
    'InterYearVariance.GrowingSeason.NPP': {
        'name': 'Inter-Year Variance Growing Season NPP',
        'category': 'Ecology',
        'units': '',
        'description': 'Variance among years in NPP for the growing season',
    },
}


_ISO_CODES = None


def iso_from_code(code):
    global _ISO_CODES
    if _ISO_CODES is None:
        _ISO_CODES = {c.iso_code: c for c in ISOCode.objects.all()}
    return _ISO_CODES.get(code)


def create_environmental_variables():
    for k, var_dict in ENVIRONMENTAL_MAP.items():
        if 'category' in var_dict:
            category, created = EnvironmentalCategory.objects.get_or_create(
                name=var_dict['category']
            )
            if created:
                logging.info("Created environmental category %s" % category)
        else:
            category = None

        obj, created = EnvironmentalVariable.objects.get_or_create(
            name=var_dict['name'],
            units=var_dict['units'],
            category=category)
        obj.codebook_info = var_dict['description']
        obj.save()
        logging.info("Saved environmental variable %s" % obj)
        yield obj.name, obj


def load_environmental(items):
    variables = dict(list(create_environmental_variables()))
    societies = {(s.ext_id, s.source_id): s for s in Society.objects.all()}
    res = 0
    for item in items:
        if _load_environmental(item, variables, societies):
            res += 1
    return res


def _load_environmental(env_dict, variables, societies):
    ext_id = env_dict['ID']
    source = get_source(env_dict['Source'])

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
        iso_code = iso_from_code(env_dict['iso'])

        # Create the base Environmental
        environmental, created = Environmental.objects.get_or_create(
            society=society,
            source=source,
            iso_code=iso_code
        )
        for k in ENVIRONMENTAL_MAP:  # keys are the columns in the CSV file
            var_dict = ENVIRONMENTAL_MAP[k]
            variable = variables.get(var_dict['name'])
            if variable is None:  # pragma: no cover
                logging.warn("Did not find an EnvironmentalVariable with name %s" % var_dict['name'])
                continue
            if env_dict[k] and env_dict[k] != 'NA':
                value = float(env_dict[k])
                EnvironmentalValue.objects.get_or_create(
                    variable=variable,
                    value=value,
                    environmental=environmental,
                    source=source)
            logging.info(
                "Created environmental value for variable %s and society %s" % (var_dict['name'], society)
            )
    else:
        environmental = found_environmentals[0]
    return environmental
