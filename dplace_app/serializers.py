from rest_framework.relations import RelatedField
from rest_framework_gis import serializers as gis_serializers
from models import *
from rest_framework import serializers

# Cultural Trait Variables
class VariableCodeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableCodeDescription
        fields = ('id', 'code', 'description', 'variable')

class VariableDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableDescription
        fields = ('id', 'label', 'name')

class VariableCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableCategory
        fields = ('id', 'name',)

class VariableDescriptionDetailSerializer(serializers.ModelSerializer):
    index_categories = VariableCategorySerializer(many=True)
    niche_categories = VariableCategorySerializer(many=True)
    class Meta:
        model = VariableDescription
        fields = ('id', 'label', 'name', 'index_categories', 'niche_categories',)

class VariableCategoryDetailSerializer(serializers.ModelSerializer):
    # Use a Primary key related field or just get the variable
    index_variables = VariableDescriptionSerializer(many=True)
    niche_variables = VariableDescriptionSerializer(many=True)
    class Meta:
        model = VariableCategory
        fields = ('id', 'name', 'index_variables','niche_variables')

class VariableCodedValueSerializer(serializers.ModelSerializer):
    code_description = VariableCodeDescriptionSerializer(source='code')
    class Meta:
        model = VariableCodedValue
        fields = ('id', 'variable', 'society', 'coded_value', 'code_description')

# ISO Codes
class ISOCodeSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = ISOCode

# Environmental Data
class EnvironmentalVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalVariable

class EnvironmentalValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentalValue

class EnvironmentalSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = Environmental

# Languages
class LanguageClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageClass

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language

class LanguageClassificationSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(source='language')
    class Meta:
        model = LanguageClassification

# Societies
class SocietySerializer(gis_serializers.GeoModelSerializer):
    iso_code = serializers.CharField(source='iso_code.iso_code')
    language = LanguageSerializer(source='language')
    class Meta:
        model = Society
        fields = ('id', 'ext_id', 'name', 'location', 'iso_code', 'language', 'source')

# Geographic Regions
class GeographicRegionSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = GeographicRegion
        fields = ('id','level_2_re','count','region_nam','continent','tdwg_code')

class LanguageTreeSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(source='languages', many=True)
    class Meta:
        model = LanguageTree
        fields = ('id','name','languages')

SEARCH_LANGUAGE = 'l'
SEARCH_ENVIRONMENTAL = 'e'
SEARCH_VARIABLES = 'v'
SEARCH_GEOGRAPHIC = 'g'

class SocietyResult(object):
    '''
    Encapsulates societies and their related search values for serializing
    '''
    def __init__(self, society):
        self.society = society
        self.variable_coded_values = set()
        self.environmental_values = set()
        self.languages = set()
        self.geographic_regions = set()
    def add_variable_coded_value(self,variable_coded_value):
        self.variable_coded_values.add(variable_coded_value)
    def add_environmental_value(self,environmental_value):
        self.environmental_values.add(environmental_value)
    def add_language(self,language):
        self.languages.add(language)
    def add_geographic_region(self,geographic_region):
        self.geographic_regions.add(geographic_region)
    def includes_criteria(self,criteria=[]):
        result = True
        if SEARCH_VARIABLES in criteria and len(self.variable_coded_values) == 0:
            result = False
        if SEARCH_ENVIRONMENTAL in criteria and len(self.environmental_values) == 0:
            result = False
        if SEARCH_LANGUAGE in criteria and len(self.languages) == 0:
            result = False
        if SEARCH_GEOGRAPHIC in criteria and len(self.geographic_regions) == 0:
            result = False
        return result

class SocietyResultSet(object):
    '''
    Provides a mapping of Societies to SocietyResult objects
    Used in building the search response
    '''

    def __init__(self):
        # Use a dictionary to map society_id -> SocietyResult
        self._society_results = dict()
        self.societies = None # not valid until finalize() is called
        # These are the column headers in the search results
        self.variable_descriptions = set()
        self.environmental_variables = set()
        self.languages = set()
        self.geographic_regions = set()

    def _get_society_result(self,society):
        if society.id not in self._society_results.keys():
            self._society_results[society.id] = SocietyResult(society)
        return self._society_results[society.id]

    def add_cultural(self,society,variable_description,variable_coded_value):
        self.variable_descriptions.add(variable_description)
        self._get_society_result(society).add_variable_coded_value(variable_coded_value)

    def add_environmental(self,society,environmental_variable,environmental_value):
        self.environmental_variables.add(environmental_variable)
        self._get_society_result(society).add_environmental_value(environmental_value)

    def add_language(self,society,language):
        self.languages.add(language)
        self._get_society_result(society).add_language(language)

    def add_geographic_region(self,society,geographic_region):
        self.geographic_regions.add(geographic_region)
        self._get_society_result(society).add_geographic_region(geographic_region)

    def finalize(self,criteria):
        self.societies = [x for x in self._society_results.values() if x.includes_criteria(criteria)]


class SocietyResultSerializer(serializers.Serializer):
    '''
    Serializer for the SocietyResult object
    '''
    society = SocietySerializer()
    variable_coded_values = VariableCodedValueSerializer(many=True)
    environmental_values = EnvironmentalValueSerializer(many=True)
    languages = LanguageSerializer(many=True)
    geographic_regions = GeographicRegionSerializer(many=True)

class SocietyResultSetSerializer(serializers.Serializer):
    '''
    Serialize a set of society results and the search criteria
    '''
    # Results contains a society and variable values that matched
    societies = SocietyResultSerializer(many=True)
    # These contain the search parameters
    # variable descriptions -> variable codes
    variable_descriptions = VariableDescriptionSerializer(many=True)
    # environmental variables -> environmental values
    environmental_variables = EnvironmentalVariableSerializer(many=True)
    # languages - Does not map to a more specific value
    languages = LanguageSerializer(many=True)
    # Geographic Regions - does not map to a more specific value
    geographic_regions = GeographicRegionSerializer(many=True)
