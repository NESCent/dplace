import csv
import sys
from django.contrib.gis.geos import Point
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from dplace_app.models import *

MISSING_CODES = []

def run(file_name=None, mode=None):
    # read the csv file
    with open(file_name, 'rb') as csvfile:
        if mode in ['iso', 'ea_soc', 'env', 'ea_vars', 'ea_vals', 'langs', 'iso_lat_long']:
            csv_reader = csv.DictReader(csvfile)
            for dict_row in csv_reader:
                if mode == 'iso':
                    load_isocode(dict_row)
                elif mode == 'iso_lat_long':
                    load_iso_lat_long(dict_row)
                elif mode == 'ea_soc':
                    load_ea_society(dict_row)
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
    if mode == 'ea_vals':
        # after loading values, populate society-level data from variable values
        postprocess_ea_societies()


# get a value from a dictionary, searching the possible keys
def get_value(dict,possible_keys):
    for key in possible_keys:
        if key in dict.keys():
            return dict[key]
    return None

def get_isocode(dict):
    # ISO Code may appear in 'ISO' column (17th Ed Missing ISO codes)
    # or the 'ISO 693-3 code' column (17th Ed - ISO 693-3 - current)
    return get_value(dict,('ISO','ISO 693-3 code'))

def load_isocode(iso_dict):
    code = get_isocode(iso_dict)
    if code is None:
        print "ISO Code not found in row, skipping"
        return
    if len(code) > 3:
        print "ISO Code '%s' too long, skipping" % code
        return
    ISOCode.objects.get_or_create(iso_code=code)

def load_iso_lat_long(iso_dict):
    code = iso_dict['ISO']
    found_code = None
    try:
        found_code = ISOCode.objects.get(iso_code=code)
    except ObjectDoesNotExist:
        print "Tried to attach Lat/Long to ISO Code %s but code not found" % code
        return
    location = Point(float(iso_dict['LMP_LON']),float(iso_dict['LMP_LAT']))
    found_code.location = location
    found_code.save()

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

def load_ea_society(society_dict):
    ext_id = society_dict['ID']
    source = 'EA'
    found_societies = Society.objects.filter(ext_id=ext_id,source=source)
    if len(found_societies) == 0:
        name = society_dict['Society_name_EA']
        iso_code = iso_from_code(society_dict['ISO693_3'])
        # Get the language
        language_name = society_dict['LangNam']
        try:
            language = Language.objects.get(name=language_name,iso_code=iso_code)
        except ObjectDoesNotExist:
            language = None
            print "Warning: Creating society record for %s but no language found with name %s" % (ext_id, language_name)
        society = Society(ext_id=ext_id,
                          name=name,
                          source=source,
                          iso_code=iso_code,
                          language=language
                          )
        society.save()

def postprocess_ea_societies():
    '''
    Some of the EA Variable values represent data that is needed at the society level, e.g.
    source and location
    '''
    try:
        lon_var = VariableDescription.objects.get(name='Longitude')
        lat_var = VariableDescription.objects.get(name='Latitude')
        focal_year_var = VariableDescription.objects.get(name='Date: Year with Century')
    except ObjectDoesNotExist:
        print "Unable to find vars for Lon/Lat/Year.  Have you loaded the ea_vars?"
    for society in Society.objects.filter(source='EA'):
        # Get location
        try:
            lon_val = society.variablecodedvalue_set.get(variable=lon_var)
            lat_val = society.variablecodedvalue_set.get(variable=lat_var)
        except ObjectDoesNotExist:
            print "Unable to get lon/lat for society %s, skipping postprocessing" % society
            continue
        try:
            location = Point(
                float(lon_val.coded_value),
                float(lat_val.coded_value)
            )
            society.location = location
        except ValueError:
            print "Unable to create Point from (%s,%s) for society %s" % (lon_val.coded_value, lat_val.coded_value, society)
            # TODO: Get source, incl focal year
        society.save()

def eavar_number_to_label(number):
    return "EA{0:0>3}".format(number)

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

    label = eavar_number_to_label(number)
    name = var_dict['Variable'].strip()
    variable, created = VariableDescription.objects.get_or_create(label=label,name=name)

    index_categories = [clean_category(x) for x in var_dict['INDEXCATEGORY'].split(',')]
    # Currently max 1 niche category
    niche_categories = [clean_category(x) for x in var_dict['NICHECATEGORY'].split(',')]

    # when creating categories, ignore '?'
    for category_name in index_categories:
        index_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.index_categories.add(index_category)
    for category_name in niche_categories:
        niche_category, created = VariableCategory.objects.get_or_create(name=category_name)
        variable.niche_categories.add(niche_category)

def clean_category(category):
    return category.strip().capitalize()

SORT_COLUMN				= 0
VARIABLE_VNUMBER_COLUMN = 1
VARIABLE_NUMBER_COLUMN 	= 2
VARIABLE_NAME_COLUMN 	= 3
N_COLUMN 				= 4
CODE_COLUMN 			= 5
DESCRIPTION_COLUMN 		= 6

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
    variable = None
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if row_is_skip(row):
            pass
        elif row_is_data(row):
            if variable is None:
                # Variable may have been excluded from D-PLACE, ignore this data row
                continue
            code = row[CODE_COLUMN].strip()
            n = row[N_COLUMN].strip()
            try:
                n = int(n)
            except ValueError:
                n = 0
            found_descriptions = VariableCodeDescription.objects.filter(variable=variable,code=code)
            if len(found_descriptions) == 0:
                # This won't help for things that specify a range or include the word or
                description = row[DESCRIPTION_COLUMN].strip()
                code_description = VariableCodeDescription(variable=variable,
                                                             code=code,
                                                             description=description,
                                                             n=n)
                code_description.save()
        elif row_is_headers(row):
            pass
        elif row_is_def(row):
            # get the variable number
            number = int(row[VARIABLE_NUMBER_COLUMN])
            try:
                # Some variables in the EA have been excluded from D-PLACE, so there
                # will be no VariableDescription object for them
                label = eavar_number_to_label(number)
                variable = VariableDescription.objects.get(label=label)
            except ObjectDoesNotExist:
                variable = None
        else:
            print "did not get anything from this row %s" % (','.join(row)).strip()

def load_ea_val(val_row):
    ext_id = val_row['ID'].strip()
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
            label = eavar_number_to_label(number)
            value = val_row[key].strip()
            try:
                variable = VariableDescription.objects.get(label=label)
            except ObjectDoesNotExist:
                continue
            try:
                # Check for Code description if it exists.
                code = VariableCodeDescription.objects.get(variable=variable,code=value)
            except ObjectDoesNotExist:
                code = None
            try:
                variable_value = VariableCodedValue(variable=variable,
                                                    society=society,
                                                    coded_value=value,
                                                    code=code)
                variable_value.save()
            except IntegrityError:
                print "Unable to store value %s for var %s in society %s, already exists" % (value, variable, society)

def load_lang(lang_row):
    # Extract values from dictionary
    code = get_isocode(lang_row)
    if code is None:
        print "ISO Code not found in row, skipping"
        return
    language_name = get_value(lang_row,('Language name','NAM'))
    ethnologue_classification = get_value(lang_row,('Ethnologue Classification (unrevised)','Ethnologue classification (if applicable)'))
    family_names = [
        get_value(lang_row,('FAMILY-REVISED','FAMILY')),
        lang_row['Class2'],
        lang_row['Class3']
    ]
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
    # Classes
    classes = []
    for i in range(3):
        level = i + 1
        name = family_names[i].strip()
        if len(name) == 0:
            # empty cell
            continue
        try:
            classes.append(LanguageClass.objects.get(level=level,name=name))
        except ObjectDoesNotExist:
            if len(classes) > 0:
                parent = classes[-1]
            else:
                parent = None
            lang_class = LanguageClass(level=level, name=name, parent=parent)
            lang_class.save()
            classes.append(lang_class)

    # Finally, create the LanguageClassification
    classification_scheme = 'R' # Ethnologue17-Revised
    try:
        classification = LanguageClassification.objects.get(ethnologue_classification=ethnologue_classification)
    except ObjectDoesNotExist:
        class_family = classes[0]
        class_subfamily = classes[1] if len(classes) > 1 else None
        class_subsubfamily = classes[2] if len(classes) > 2 else None
        classification = LanguageClassification(scheme=classification_scheme,
                                                language=language,
                                                ethnologue_classification=ethnologue_classification,
                                                class_family=class_family,
                                                class_subfamily=class_subfamily,
                                                class_subsubfamily=class_subsubfamily,
                                                )
        classification.save()

def add_missing_isocode(isocode):
    MISSING_CODES.append(isocode)

if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
