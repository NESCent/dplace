from rest_framework import serializers

from dplace_app import models

# constants for SocietyResult
SEARCH_LANGUAGE = 'l'
SEARCH_ENVIRONMENTAL = 'e'
SEARCH_VARIABLES = 'v'
SEARCH_GEOGRAPHIC = 'g'


class SourceSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Source


# Cultural Trait Variables
class CulturalCodeDescriptionSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.CulturalCodeDescription
        fields = ('id', 'code', 'description', 'short_description', 'variable')


class CulturalVariableSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.CulturalVariable
        fields = (
            'id',
            'label',
            'name',
            'codebook_info',
            'data_type',
            'source',
            'index_categories',
            'units'
        )


class CulturalCategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.CulturalCategory
        fields = ('id', 'name',)


class CulturalVariableDetailSerializer(serializers.ModelSerializer):
    index_categories = CulturalCategorySerializer(many=True)
    niche_categories = CulturalCategorySerializer(many=True)

    class Meta(object):
        model = models.CulturalVariable
        fields = (
            'id', 'label', 'name', 'index_categories', 'niche_categories'
        )


class CulturalCategoryDetailSerializer(serializers.ModelSerializer):
    # Use a Primary key related field or just get the variable
    index_variables = CulturalVariableSerializer(many=True)
    niche_variables = CulturalVariableSerializer(many=True)

    class Meta(object):
        model = models.CulturalCategory
        fields = ('id', 'name', 'index_variables', 'niche_variables')


class CulturalValueSerializer(serializers.ModelSerializer):
    code_description = CulturalCodeDescriptionSerializer(source='code')
    references = SourceSerializer(many=True)

    class Meta(object):
        model = models.CulturalValue
        fields = (
            'id',
            'variable',
            'society',
            'coded_value',
            'code_description',
            'source',
            'references',
            'subcase',
            'focal_year',
            'comment'
        )


class ISOCodeSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.ISOCode


class EnvironmentalCategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.EnvironmentalCategory


class EnvironmentalVariableSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.EnvironmentalVariable


class EnvironmentalValueSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.EnvironmentalValue


class LanguageFamilySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.LanguageFamily


class LanguageSerializer(serializers.ModelSerializer):
    iso_code = serializers.CharField(source='iso_code.iso_code')
    family = LanguageFamilySerializer()

    class Meta(object):
        model = models.Language
        fields = (
            'id',
            'name',
            'glotto_code',
            'iso_code',
            'family',
        )


class LanguageSerializerWithSocieties(serializers.ModelSerializer):
    iso_code = serializers.CharField(source='iso_code.iso_code')
    family = LanguageFamilySerializer()

    class Meta(object):
        model = models.Language
        fields = (
            'id',
            'name',
            'glotto_code',
            'iso_code',
            'family',
            'societies',
        )


class SocietySerializer(serializers.ModelSerializer):
    language = LanguageSerializer()
    source = SourceSerializer()

    class Meta(object):
        model = models.Society
        fields = (
            'id',
            'ext_id',
            'xd_id',
            'name',
            'original_name',
            'alternate_names',
            'location',
            'original_location',
            'language',
            'focal_year',
            'source'
        )


class GeographicRegionSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.GeographicRegion
        fields = (
            'id', 'level_2_re', 'count', 'region_nam', 'continent', 'tdwg_code'
        )


class SocietyWithRegionSerializer(SocietySerializer):
    region = GeographicRegionSerializer()

    def __init__(self):
        super(SocietyWithRegionSerializer, self).__init__()
        self.Meta.fields = list(SocietySerializer.Meta.fields) + ['region']


class TreeSocietySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Society
        fields = ('id', 'ext_id', 'name')


class LanguageTreeLabelsSequenceSerializer(serializers.HyperlinkedModelSerializer):
    society = TreeSocietySerializer()
    labels = serializers.ReadOnlyField(source='labels.label')
    
    class Meta:
        model = models.LanguageTreeLabelsSequence
        fields = ('society', 'labels', 'fixed_order')


class LanguageTreeLabelsSerializer(serializers.ModelSerializer):
    societies = LanguageTreeLabelsSequenceSerializer(source='languagetreelabelssequence_set', many=True)

    class Meta(object):
        model = models.LanguageTreeLabels
        fields = ('id', 'languageTree', 'label', 'language', 'societies')


class LanguageTreeSerializer(serializers.ModelSerializer):
    taxa = LanguageTreeLabelsSerializer(many=True)

    class Meta(object):
        model = models.LanguageTree
        fields = ('id', 'name', 'taxa', 'newick_string')
        

class SocietyResult(object):
    """
    Encapsulates societies and their related search values for serializing
    """
    def __init__(self, society):
        self.society = society
        self.variable_coded_values = set()
        self.environmental_values = set()

    def __eq__(self, other):
        return self.society.id == other.society.id


class VariableCode(object):
    """
    Encapsulates societies and their related search values for serializing
    """
    def __init__(self, codes, variable):
        self.codes = codes
        self.variable = variable

    def __eq__(self, other):
        return self.variable.id == other.variable.id


class SocietyResultSet(object):
    """
    Provides a mapping of Societies to SocietyResult objects
    Used in building the search response
    """

    def __init__(self):
        self.societies = set()
        # These are the column headers in the search results
        self.variable_descriptions = set()
        self.environmental_variables = set()
        self.languages = set()
        self.geographic_regions = set()
        self.language_trees = set()


class VariableCodeSerializer(serializers.Serializer):
    codes = CulturalCodeDescriptionSerializer(many=True)
    variable = CulturalVariableSerializer()


class SocietyResultSerializer(serializers.Serializer):
    "Serializer for the SocietyResult object"
    society = SocietyWithRegionSerializer()
    variable_coded_values = CulturalValueSerializer(many=True)
    environmental_values = EnvironmentalValueSerializer(many=True)


class SocietyResultSetSerializer(serializers.Serializer):
    "Serialize a set of society results and the search criteria"
    # Results contains a society and variable values that matched
    societies = SocietyResultSerializer(many=True)
    # These contain the search parameters
    # variable descriptions -> variable codes
    variable_descriptions = VariableCodeSerializer(many=True)
    # environmental variables -> environmental values
    environmental_variables = EnvironmentalVariableSerializer(many=True)
    # languages - Does not map to a more specific value
    languages = LanguageSerializer(many=True)
    # Geographic Regions - does not map to a more specific value
    geographic_regions = GeographicRegionSerializer(many=True)
    # language trees for this society result set
    language_trees = LanguageTreeSerializer(many=True)


class Legend(object):
    def __init__(self, name, svg):
        self.name = name
        self.svg = svg


class LegendSerializer(serializers.Serializer):
    name = serializers.CharField()
    svg = serializers.CharField()


class ZipResultSet(object):
    def __init__(self):
        self.tree = None
        self.name = None
        self.legends = []


class ZipResultSetSerializer (serializers.Serializer):
    tree = serializers.CharField()
    name = serializers.CharField()
    legends = LegendSerializer(many=True)
