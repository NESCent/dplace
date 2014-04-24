# -*- coding: utf-8 -*-
# __author__ = 'dan'
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *

ENVIRONMENTAL_MAP = {
    'AnnualMeanTemperature': {
        'name': 'Annual Mean Temperature',
        'units': '℃',
    },
    'AnnualTemperatureVariance': {
        'name': 'Annual Temperature Variance',
        'units': '℃',
    },
    'TemperatureConstancy': {
        'name': 'Temperature Constancy',
        'units': '',
    },
    'TemperatureContingency': {
        'name': 'Temperature Contingency',
        'units': '',
    },
    'TemperaturePredictability': {
        'name': 'Temperature Predictability',
        'units': '',
    },
    'AnnualMeanPrecipitation': {
        'name': 'Annual Mean Precipitation',
        'units': 'mm',
    },
    'AnnualPrecipitationVariance': {
        'name': 'Annual Precipitation Variance',
        'units': '',
    },
    'PrecipitationConstancy': {
        'name': 'Precipitation Constancy',
        'units': '',
    },
    'PrecipitationContingency': {
        'name': 'Precipitation Contingency',
        'units': '',
    },
    'PrecipitationPredictability': {
        'name': 'Precipitation Predictability',
        'units': '',
    },
    'BirdRichness': {
        'name': 'Bird Richness',
        'units': '',
    },
    'MammalRichness': {
        'name': 'Mammal Richness',
        'units': '',
    },
    'AmphibianRichness': {
        'name': 'Amphibian Richness',
        'units': '',
    },
    'VascularPlantsRichness': {
        'name': 'Vascular Plants Richness',
        'units': '',
    },
    # TODO: EcoRegion! (text)
    'Elevation': {
        'name': 'Elevation',
        'units': '',
    },
    'Slope': {
        'name': 'Slope',
        'units': '',
    },
    # TODO: Coastal (Bool)
    'NetPrimaryProduction': {
        'name': 'Net Primary Production',
        'units': '',
    },
    'DurationOfGrowingSeason': {
        'name': 'Duration of Growing Season',
        'units': 'mo',
    },
    'MeanGrowingSeason.NPP': {
        'name': 'Mean Growing Season NPP',
        'units': '',
    },
    'InterYearVariance.GrowingSeason.NPP': {
        'name': 'Inter-Year Variance Growing Season NPP',
        'units': '',
    },
}

def iso_from_code(code):
    if code == 'NA':
        return None
    try:
        return ISOCode.objects.get(iso_code=code)
    except ObjectDoesNotExist:
        return None

def create_environmental_variables():
    for k in ENVIRONMENTAL_MAP:
        var_dict = ENVIRONMENTAL_MAP[k]
        EnvironmentalVariable.objects.get_or_create(name=var_dict['name'],units=var_dict['units'])

def load_environmental(env_dict):
    ext_id = env_dict['ID']
    source = env_dict['Source']

    # hack for B109 vs. 109
    if source == 'Binford' and ext_id.find('B') == -1:
        ext_id = 'B' + ext_id

    try:
        society = Society.objects.get(ext_id=ext_id, source=source)
    except ObjectDoesNotExist:
        print "Unable to find a Society object with ext_id %s and source %s, skipping..." % (ext_id, source)
        return
    # This limits the environmental data to one record per society record
    found_environmentals = Environmental.objects.filter(society=society)
    if len(found_environmentals) == 0:
        reported_latlon =  Point(float(env_dict['Orig.longitude']),float(env_dict['Orig.latitude']))
        actual_latlon = Point(float(env_dict['longitude']), float(env_dict['latitude']))
        iso_code = iso_from_code(env_dict['iso'])

        # Create the base Environmental
        environmental = Environmental(society=society,
                                      reported_location=reported_latlon,
                                      actual_location=actual_latlon,
                                      iso_code=iso_code)
        environmental.save()
        for k in ENVIRONMENTAL_MAP: # keys are the columns in the CSV file
            var_dict = ENVIRONMENTAL_MAP[k]
            try:
                # Get the variable
                variable = EnvironmentalVariable.objects.get(name=var_dict['name'])
            except ObjectDoesNotExist:
                print "Warning: Did not find an EnvironmentalVariable with name %s" % var_dict['name']
                continue
            if env_dict[k] and env_dict[k] != 'NA':
                value = float(env_dict[k])
                EnvironmentalValue.objects.get_or_create(variable=variable,value=value,environmental=environmental)
