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
            'index_categories'
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


class EnvironmentalSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.Environmental


class LanguageFamilySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = models.LanguageFamily


class LanguageSerializer(serializers.ModelSerializer):
    # glotto_code = serializers.CharField(source='glotto_code')
    iso_code = serializers.CharField(source='iso_code.iso_code')
    family = LanguageFamilySerializer()
    count = serializers.SerializerMethodField()
    
    def get_count(self, language):
        return models.Society.objects.all().filter(language=language).count()

    class Meta(object):
        model = models.Language
        fields = (
            'id',
            'name',
            'glotto_code',
            'iso_code',
            'family',
            'count',
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
            'location',
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


class LanguageTreeSerializer(serializers.ModelSerializer):
    languages = LanguageSerializer(many=True)

    class Meta(object):
        model = models.LanguageTree
        fields = ('id', 'name', 'languages', 'newick_string')


class SocietyResult(object):
    """
    Encapsulates societies and their related search values for serializing
    """
    def __init__(self, society):
        self.society = society
        self.variable_coded_values = set()
        self.environmental_values = set()
        self.languages = set()
        self.geographic_regions = set()

    def add_variable_coded_value(self, variable_coded_value):
        self.variable_coded_values.add(variable_coded_value)

    def add_environmental_value(self, environmental_value):
        self.environmental_values.add(environmental_value)

    def add_language(self, language):
        self.languages.add(language)

    def add_geographic_region(self, geographic_region):
        self.geographic_regions.add(geographic_region)

    def includes_criteria(self, criteria=None):
        if not criteria:
            return True
        if SEARCH_VARIABLES in criteria and len(self.variable_coded_values) == 0:
            return False
        if SEARCH_ENVIRONMENTAL in criteria and len(self.environmental_values) == 0:
            return False
        if SEARCH_LANGUAGE in criteria and len(self.languages) == 0:
            return False
        if SEARCH_GEOGRAPHIC in criteria and len(self.geographic_regions) == 0:
            return False
        return True


class VariableCode(object):
    """
    Encapsulates societies and their related search values for serializing
    """
    def __init__(self, codes, variable):
        self.codes = codes
        self.variable = variable


class SocietyResultSet(object):
    """
    Provides a mapping of Societies to SocietyResult objects
    Used in building the search response
    """

    def __init__(self):
        # Use a dictionary to map society_id -> SocietyResult
        self._society_results = dict()
        self._codes = dict()
        self.societies = None  # not valid until finalize() is called
        # These are the column headers in the search results
        self.variable_descriptions = None
        self.environmental_variables = set()
        self.languages = set()
        self.geographic_regions = set()
        self.language_trees = set()

    def _get_society_result(self, society):
        if society.id not in self._society_results.keys():
            self._society_results[society.id] = SocietyResult(society)
        return self._society_results[society.id]
        
    def add_code(self, codes, variable):
        if variable.id not in self._codes.keys():
            self._codes[variable.id] = VariableCode(codes, variable)

    def add_cultural(self, society, description, codes, value):
        self._get_society_result(society).add_variable_coded_value(value)
        self.add_code(codes, description)
        
    def add_environmental(self, society, variable, value):
        self.environmental_variables.add(variable)
        self._get_society_result(society).add_environmental_value(value)

    def add_language(self, society, language):
        self.languages.add(language)
        self._get_society_result(society).add_language(language)

    def add_geographic_region(self, society, region):
        self.geographic_regions.add(region)
        self._get_society_result(society).add_geographic_region(region)
   
    def add_language_tree(self, language_tree):
        self.language_trees.add(language_tree)
    
    def finalize(self, criteria):
        self.societies = [
            x for x in self._society_results.values() if x.includes_criteria(criteria)
        ]
        self.variable_descriptions = [x for x in self._codes.values()]


class VariableCodeSerializer(serializers.Serializer):
    codes = CulturalCodeDescriptionSerializer(many=True)
    variable = CulturalVariableSerializer()


class SocietyResultSerializer(serializers.Serializer):
    "Serializer for the SocietyResult object"
    society = SocietySerializer()
    variable_coded_values = CulturalValueSerializer(many=True)
    environmental_values = EnvironmentalValueSerializer(many=True)
    languages = LanguageSerializer(many=True)
    geographic_regions = GeographicRegionSerializer(many=True)


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
