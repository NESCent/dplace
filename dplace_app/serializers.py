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

class LanguageClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageClassification

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language

# Societies
class SocietySerializer(gis_serializers.GeoModelSerializer):
    iso_code = serializers.CharField(source='iso_code.iso_code')
    class Meta:
        model = Society
        fields = ('id', 'ext_id', 'name', 'location', 'iso_code', 'source')

SEARCH_LANGUAGE = 'l'
SEARCH_ENVIRONMENTAL = 'e'
SEARCH_VARIABLES = 'v'

class SocietyResult(object):
    '''
    Encapsulates societies and their related search values for serializing
    '''
    def __init__(self, society):
        self.society = society
        self.variable_coded_values = set()
        self.environmental_values = set()
        self.language_classifications = set()
    def add_variable_coded_value(self,variable_coded_value):
        self.variable_coded_values.add(variable_coded_value)
    def add_environmental_value(self,environmental_value):
        self.environmental_values.add(environmental_value)
    def add_language_classification(self,language_classification):
        self.language_classifications.add(language_classification)
    def includes_criteria(self,criteria=[]):
        result = True
        if SEARCH_VARIABLES in criteria and len(self.variable_coded_values) == 0:
            result = False
        if SEARCH_ENVIRONMENTAL in criteria and len(self.environmental_values) == 0:
            result = False
        if SEARCH_LANGUAGE in criteria and len(self.language_classifications) == 0:
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
        self.results = None # not valid until finalize() is called
        # These are the column headers in the search results
        self.variable_descriptions = set()
        self.environmental_variables = set()
        self.language_classes = set()

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

    def add_language(self,society,language_class,language_classification):
        self.language_classes.add(language_class)
        self._get_society_result(society).add_language_classification(language_classification)

    def finalize(self,criteria):
        self.results = [x for x in self._society_results.values() if x.includes_criteria(criteria)]


class SocietyResultSerializer(serializers.Serializer):
    '''
    Serializer for the SocietyResult object
    '''
    society = SocietySerializer()
    variable_coded_values = VariableCodedValueSerializer(many=True)
    environmental_values = EnvironmentalValueSerializer(many=True)
    language_classifications = LanguageClassificationSerializer(many=True)

class SocietyResultSetSerializer(serializers.Serializer):
    '''
    Serialize a set of society results and the search criteria
    '''
    # Results contains a society and variable values that matched
    results = SocietyResultSerializer(many=True)
    # These contain the search parameters
    # variable descriptions -> variable codes
    variable_descriptions = VariableDescriptionSerializer(many=True)
    # environmental variables -> environmental values
    environmental_variables = EnvironmentalVariableSerializer(many=True)
    # language classes -> language classifications
    language_classes = LanguageClassSerializer(many=True)
