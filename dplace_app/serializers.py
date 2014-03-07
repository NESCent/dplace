from rest_framework.relations import RelatedField
from rest_framework_gis import serializers as gis_serializers
from models import *
from rest_framework import serializers

class VariableCodeDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableCodeDescription
        fields = ('id', 'code', 'description', 'variable')

class VariableDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableDescription
        fields = ('id', 'label', 'name')

class VariableCodedValueSerializer(serializers.ModelSerializer):
    code_description = VariableCodeDescriptionSerializer(source='code')
    class Meta:
        model = VariableCodedValue
        fields = ('id', 'variable', 'society', 'coded_value', 'code_description')

class ISOCodeSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = ISOCode

class SocietySerializer(gis_serializers.GeoModelSerializer):
    iso_code = serializers.CharField(source='iso_code.iso_code')
    class Meta:
        model = Society
        fields = ('id', 'ext_id', 'name', 'location', 'iso_code', 'source')

class EnvironmentalSerializer(gis_serializers.GeoModelSerializer):
    class Meta:
        model = Environmental

class LanguageClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageClass

class LanguageClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageClassification

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language