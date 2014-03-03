import csv
import sys
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from dplace_app.models import *

MISSING_CODES = []

def run(file_name=None, mode=None):
    # read the csv file
    with open(file_name, 'rb') as csvfile:
        if mode in ['iso', 'soc', 'env', 'ea_vars', 'ea_vals', 'langs']:
            csv_reader = csv.DictReader(csvfile)
            for dict_row in csv_reader:
                if mode == 'iso':
                    load_isocode(dict_row)
                elif mode == 'soc':
                    load_society(dict_row)
                elif mode == 'env':
                    load_environmental(dict_row)
                elif mode == 'ea_vars':
                    load_ea_var(dict_row)
                elif mode == 'ea_vals':
                    load_ea_val(dict_row)
                elif mode == 'langs':
                    load_lang(dict_row)
        elif mode == 'ea_codes':
            load_ea_codes(csvfile)
    if len(MISSING_CODES) > 0:
        print "Missing ISO Codes:"
        print '\n'.join(MISSING_CODES)


def load_isocode(iso_dict):
    code = iso_dict['ISO']
    found_codes = ISOCode.objects.filter(iso_code=code)
    if len(found_codes) == 0:
        lonlat = Point(float(iso_dict['LMP_LON']),float(iso_dict['LMP_LAT']))
        isocode = ISOCode(iso_code=code,location=lonlat)
        isocode.save()

# These are all floats
ENVIRONMENTAL_MAP = {
    'AnnualMeanTemperature': 'annual_mean_temperature',
    'AnnualTemperatureVariance': 'annual_temperature_variance',
    'TemperatureConstancy': 'temperature_constancy',
    'TemperatureContingency': 'temperature_contingency',
    'TemperaturePredictability': 'temperature_predictability',
    'AnnualMeanPrecipitation': 'annual_mean_precipitation',
    'AnnualPrecipitationVariance': 'annual_precipitation_variance',
    'PrecipitationConstancy': 'precipitation_constancy',
    'PrecipitationContingency': 'precipitation_contingency',
    'PrecipitationPredictability': 'precipitation_predictability',
    'MeanGrowingSeason_duration': 'mean_growing_season_duration',
    'NetPrimaryProductivity': 'net_primary_productivity',
    'BirdDiversity': 'bird_diversity',
    'MammalDiversity': 'mammal_diversity',
    'AmphibianDiversity': 'amphibian_diversity',
    'PlantDiversity': 'plant_diversity',
    'Elevation': 'elevation',
    'Slope': 'slope',
}

def iso_from_code(code):
    if code == 'NA':
        return None
    try:
        return ISOCode.objects.get(iso_code=code)
    except ObjectDoesNotExist:
        return None

def load_environmental(env_dict):
    ext_id = env_dict['id']
    source = env_dict['source']

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
        reported_latlon =  Point(float(env_dict['Reported_Lon']),float(env_dict['Reported_Lat']))
        actual_latlon = Point(float(env_dict['longitude']), float(env_dict['latitude']))
        iso_code = iso_from_code(env_dict['iso'])

        environmental = Environmental(society=society,
                                      reported_location=reported_latlon,
                                      actual_location=actual_latlon,
                                      iso_code=iso_code)
        for k in ENVIRONMENTAL_MAP:
            v = ENVIRONMENTAL_MAP[k]
            if env_dict[k]:
                if env_dict[k] != 'NA':
                    setattr(environmental, v, float(env_dict[k]))
        environmental.save()

def load_society(society_dict):
    ext_id = society_dict['id']
    source = society_dict['source']
    found_societies = Society.objects.filter(ext_id=ext_id,source=source)
    if len(found_societies) == 0:
        name = society_dict['society_name']
        location = Point(float(society_dict['long']),float(society_dict['lat']))
        iso_code = iso_from_code(society_dict['iso'])
        society = Society(ext_id=ext_id,
                          name=name,
                          location=location,
                          source=source,
                          iso_code=iso_code,
                          )
        society.save()

def load_ea_var(var_dict):
    """
    Variables are loaded form ea_variable_names.csv for simplicity,
    but there is more detailed information in ea_codes.csv
    """
    try:
        number = int(var_dict['Variable number'])
    except ValueError:
        return
    exclude = var_dict['Exclude from D-PLACE?']
    if exclude == '1':
        return

    found_vars = EAVariableDescription.objects.filter(number=number)
    if len(found_vars) == 0:
        name = var_dict['Variable'].strip()
        variable = EAVariableDescription(number=number,
                                         name=name)
        variable.save()

SORT_COLUMN				= 0
VARIABLE_NUMBER_COLUMN 	= 1
VARIABLE_NAME_COLUMN 	= 2
N_COLUMN 				= 3
CODE_COLUMN 			= 4
DESCRIPTION_COLUMN 		= 5

# e.g. N	CODE	DESCRIPTION
def row_is_headers(row):
    possible_code = row[CODE_COLUMN].strip()
    possible_n = row[N_COLUMN].strip()
    possible_desc = row[DESCRIPTION_COLUMN].strip()
    if possible_code == 'CODE' and possible_n == 'N' and possible_desc == 'DESCRIPTION':
        return True
    else:
        return False

# e.g. 1	1	Gathering 	1267
def row_is_def(row):
    possible_number = row[VARIABLE_NUMBER_COLUMN].strip()
    if possible_number.isdigit():
        return True
    else:
        return False

# has a code value and a description text
# e.g. 706	0	0 - 5% Dependence
def row_is_data(row):
    # N_row is numeric
    n_cell = row[N_COLUMN].strip()
    # variable_number is empty
    number_cell = row[VARIABLE_NUMBER_COLUMN].strip()
    # Code may be ., 0, or abc... so it's not a simple identifier
    if n_cell.isdigit() and len(number_cell) == 0:
        return True
    else:
        return False

# Junk rows
def row_is_skip(row):
    sort_cell = row[SORT_COLUMN].strip()
    if sort_cell.isdigit():
        return False
    else:
        return True

def load_ea_codes(csvfile=None):
    number = None
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row_is_skip(row):
            pass
        elif row_is_data(row):
            # FIXME: Code 92 is special
            if number == 92:
                continue
            code = row[CODE_COLUMN].strip()
            found_descriptions = EAVariableCodeDescription.objects.filter(variable=variable,code=code)
            if len(found_descriptions) == 0:
                # This won't help for things that specify a range or include the word or
                description = row[DESCRIPTION_COLUMN].strip()
                code_description = EAVariableCodeDescription(variable=variable,
                                                             code=code,
                                                             description=description)
                code_description.save()
        elif row_is_headers(row):
            pass
        elif row_is_def(row):
            # get the variable number
            number = int(row[VARIABLE_NUMBER_COLUMN])
            variable = EAVariableDescription.objects.get(number=number)
        else:
            print "did not get anything from this row %s" % (','.join(row)).strip()

def load_ea_val(val_row):
    ext_id = val_row['EA_id'].strip()
    # find the existing society
    try:
        society = Society.objects.get(ext_id=ext_id)
    except ObjectDoesNotExist:
        print "Attempting to load EA values for %s but did not find an existing Society object" % ext_id
        return
    # get the keys that start with v
    for key in val_row.keys():
        if key.find('v') == 0:
            number = int(key[1:])
            value = val_row[key].strip()
            try:
                variable = EAVariableDescription.objects.get(number=number)
            except ObjectDoesNotExist:
                print "Attempting to load EA values for variable %d but did not find an existing EAVariableDescription object" % number
                continue
            try:
                # Check for Code description if it exists.
                code = EAVariableCodeDescription.objects.get(variable=variable,code=value)
            except ObjectDoesNotExist:
                code = None
            variable_value = EAVariableCodedValue(variable=variable,
                                                  society=society,
                                                  coded_value=value,
                                                  code=code)
            variable_value.save()

def load_lang(lang_row):
    # Extract values from dictionary
    code = lang_row['ISO 693-3 code']
    language_name = lang_row['Language name']
    family_name = lang_row['FAMILY-CORRECTED']
    classification_name = lang_row['Classification']
    class_names = [lang_row['Class1'], lang_row['Class2'], lang_row['Class3']]

    # ISO Code
    isocode = iso_from_code(code) # Does not create new ISO Codes
    if isocode is None:
        print "No ISO Code found in database for %s, skipping language %s" % (code, language_name)
        add_missing_isocode(code)
        return

    # Language
    try:
        language = Language.objects.get(iso_code=isocode)
    except ObjectDoesNotExist:
        language = Language(name=language_name,
                            iso_code=isocode
                            )
        language.save()
    # Family
    try:
        family = LanguageFamily.objects.get(name=family_name)
    except ObjectDoesNotExist:
        family = LanguageFamily(name=family_name)
        family.save()

    # Classes
    classes = []
    for i in range(3):
        level = i + 1
        try:
            classes.append(LanguageClass.objects.get(level=level,name=class_names[i]))
        except ObjectDoesNotExist:
            if len(classes) > 0:
                parent = classes[-1]
            else:
                parent = None
            lang_class = LanguageClass(level=level, name=class_names[i], parent=parent)
            lang_class.save()
            classes.append(lang_class)

    # Finally, create the LanguageClassification
    classification_scheme = 'R' # Ethnologue17-Revised
    try:
        classification = LanguageClassification.objects.get(name=classification_name)
    except ObjectDoesNotExist:
        classification = LanguageClassification(scheme=classification_scheme,
                                                language=language,
                                                name=classification_name,
                                                family=family,
                                                class_family=classes[0],
                                                class_subfamily=classes[1],
                                                class_subsubfamily=classes[2],
                                                )
        classification.save()

def add_missing_isocode(isocode):
    MISSING_CODES.append(isocode)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
