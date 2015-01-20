# -*- coding: utf-8 -*-
# __author__ = 'dan'
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *
from sources import get_source

ENVIRONMENTAL_MAP = {
    'AnnualMeanTemperature': {
        'name': 'Annual Mean Temperature',
        'category': 'Climate',
        'units': '°C',
    },
    'AnnualTemperatureVariance': {
        'name': 'Annual Temperature Variance',
        'category': 'Climate',
        'units': '°C',
    },
    'TemperatureConstancy': {
        'name': 'Temperature Constancy',
        'category': 'Climate',
        'units': '',
    },
    'TemperatureContingency': {
        'name': 'Temperature Contingency',
        'category': 'Climate',
        'units': '',
    },
    'TemperaturePredictability': {
        'name': 'Temperature Predictability',
        'category': 'Climate',
        'units': '',
    },
    'AnnualMeanPrecipitation': {
        'name': 'Annual Mean Precipitation',
        'category': 'Climate',
        'units': 'mm',
    },
    'AnnualPrecipitationVariance': {
        'name': 'Annual Precipitation Variance',
        'category': 'Climate',
        'units': '',
    },
    'PrecipitationConstancy': {
        'name': 'Precipitation Constancy',
        'category': 'Climate',
        'units': '',
    },
    'PrecipitationContingency': {
        'name': 'Precipitation Contingency',
        'category': 'Climate',
        'units': '',
    },
    'PrecipitationPredictability': {
        'name': 'Precipitation Predictability',
        'category': 'Climate',
        'units': '',
    },
    'BirdRichness': {
        'name': 'Bird Richness',
        'category': 'Ecology',
        'units': '',
    },
    'MammalRichness': {
        'name': 'Mammal Richness',
        'category': 'Ecology',
        'units': '',
    },
    'AmphibianRichness': {
        'name': 'Amphibian Richness',
        'category': 'Ecology',
        'units': '',
    },
    'VascularPlantsRichness': {
        'name': 'Vascular Plants Richness',
        'category': 'Ecology',
        'units': '',
    },
    # TODO: EcoRegion! (text)
    'Elevation': {
        'name': 'Elevation',
        'category': 'Physical landscape',
        'units': '',
    },
    'Slope': {
        'name': 'Slope',
        'category': 'Physical landscape',
        'units': '',
    },
    # TODO: Coastal (Bool)
    'NetPrimaryProduction': {
        'name': 'Net Primary Production',
        'category': 'Ecology',
        'units': '',
    },
    'DurationOfGrowingSeason': {
        'name': 'Duration of Growing Season',
        'category': 'Climate',
        'units': 'mo',
    },
    'MeanGrowingSeason.NPP': {
        'name': 'Mean Growing Season NPP',
        'category': 'Ecology',
        'units': '',
    },
    'InterYearVariance.GrowingSeason.NPP': {
        'name': 'Inter-Year Variance Growing Season NPP',
        'category': 'Ecology',
        'units': '',
    },
}

def iso_from_code(code):
    if code == 'NA' or len(code) == 0:
        return None
    try:
        return ISOCode.objects.get(iso_code=code)
    except ObjectDoesNotExist:
        return None

def create_environmental_variables():
    for k in ENVIRONMENTAL_MAP:
        var_dict = ENVIRONMENTAL_MAP[k]
        if 'category' in var_dict:
            env_category, created = EnvironmentalCategory.objects.get_or_create(name=var_dict['category'])
            obj, created = EnvironmentalVariable.objects.get_or_create(name=var_dict['name'],units=var_dict['units'])
            obj.category = env_category
            obj.save()
        else:
            EnvironmentalVariable.objects.get_or_create(name=var_dict['name'],units=var_dict['units']) 

def load_environmental(env_dict):
    ext_id = env_dict['ID']
    source = get_source(env_dict['Source'])

    # hack for B109 vs. 109
    if source.author == 'Binford' and ext_id.find('B') == -1:
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
                                      source=source,
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
                EnvironmentalValue.objects.get_or_create(variable=variable,value=value,
                    environmental=environmental, source=source
                )
