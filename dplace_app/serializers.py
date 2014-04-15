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

class SocietyResultMap(object):
    '''
    Provides a mapping of Societies to SocietyResult objects
    Used in building the search response
    '''
    def __init__(self):
        # Use a dictionary to map society_id -> SocietyResult
        self.society_results = dict()
    def get_society_result(self,society):
        if society.id not in self.society_results.keys():
            self.society_results[society.id] = SocietyResult(society)
        return self.society_results[society.id]
    def add_variable_coded_value(self,society,variable_coded_value):
        self.get_society_result(society).add_variable_coded_value(variable_coded_value)
    def add_environmental_value(self,society,environmental_value):
        self.get_society_result(society).add_environmental_value(environmental_value)
    def add_language_classification(self,society,language_classification):
        self.get_society_result(society).add_language_classification(language_classification)
    def get_society_results(self):
        return self.society_results.values()

class SocietyResultSerializer(serializers.Serializer):
    '''
    Serializer, uses the SocietyResult object
    '''
    society = SocietySerializer()
    variable_coded_values = VariableCodedValueSerializer(many=True)
    environmental_values = EnvironmentalValueSerializer(many=True)
    language_classifications = LanguageClassificationSerializer(many=True)
