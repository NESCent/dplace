from models import *
from rest_framework import viewsets
from serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.views import Request, Response

# Resource routes
class VariableDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableDescriptionSerializer
    filter_fields = ('label', 'name', 'index_categories', 'niche_categories',)
    queryset = VariableDescription.objects.all()
    # Override retrieve to use the detail serializer, which includes categories
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = VariableDescriptionDetailSerializer(self.object)
        return Response(serializer.data)

class VariableCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableCategorySerializer
    filter_fields = ('name', 'index_variables', 'niche_variables',)
    queryset = VariableCategory.objects.all()
    # Override retrieve to use the detail serializer, which includes variables
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = VariableCategoryDetailSerializer(self.object)
        return Response(serializer.data)


class VariableCodeDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableCodeDescriptionSerializer
    filter_fields = ('variable', 'code', 'description',)
    queryset = VariableCodeDescription.objects.all()

# Can filter by code, code__variable, or society
class VariableCodedValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableCodedValueSerializer
    filter_fields = ('variable','coded_value','code','society','code',)
    # Avoid additional database trips by select_related for foreign keys
    queryset = VariableCodedValue.objects.select_related('variable').select_related('code').all()

class SocietyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocietySerializer
    queryset = Society.objects.all()

class ISOCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ISOCodeSerializer
    filter_fields = ('iso_code',)
    queryset = ISOCode.objects.all()

class EnvironmentalVariableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalVariableSerializer
    filter_fields = ('name', 'units',)
    queryset = EnvironmentalVariable.objects.all()

class EnvironmentalValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalValueSerializer
    filter_fields = ('variable','environmental',)
    queryset = EnvironmentalValue.objects.all()

class EnvironmentalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalSerializer
    filter_fields = ('society', 'iso_code',)
    queryset = Environmental.objects.all()

class LanguageClassViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageClassSerializer
    filter_fields = ('level', 'parent', 'name',)
    model = LanguageClass

# Need an API to get classifications / languages for a class

class LanguageClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageClassificationSerializer
    filter_fields = ('scheme', 'language', 'class_family', 'class_subfamily', 'class_subsubfamily',)
    queryset = LanguageClassification.objects.all()

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageSerializer
    filter_fields = ('name', 'iso_code', 'society',)
    queryset = Language.objects.all()

# search/filter APIs
@api_view(['POST'])
@permission_classes((AllowAny,))
def find_societies(request):
    """
    View to find the societies that match an input request.  Currently expects
    { language_filters: [{language_ids: [1,2,3]}], variable_codes: [4,5,6...],
    environmental_filters: [{id: 1, operator: 'gt', params: [0.0]}, {id:3, operator 'inrange', params: [10.0,20.0] }] }

    Returns serialized collection of SocietyResult objects
    """
    result_set = SocietyResultSet()
    # Criteria keeps track of what types of data were searched on, so that we can
    # AND them together
    criteria = []

    if 'language_filters' in request.DATA:
        criteria.append(SEARCH_LANGUAGE)
        language_filters = request.DATA['language_filters']
        for filter in language_filters:
            language_ids = [int(x) for x in filter['language_ids']]
            languages = Language.objects.filter(pk__in=language_ids) # Returns a queryset
            languages.select_related('societies')
            for language in languages:
                for society in language.societies.all():
                    result_set.add_language(society,language)

    if 'variable_codes' in request.DATA:
        criteria.append(SEARCH_VARIABLES)
        # Now get the societies from variables
        variable_code_ids = [int(x) for x in request.DATA['variable_codes']]
        codes = VariableCodeDescription.objects.filter(pk__in=variable_code_ids) # returns a queryset
        coded_value_ids = []
        # Aggregate all the coded values for each selected code
        for code in codes:
            coded_value_ids += code.variablecodedvalue_set.values_list('id', flat=True)
        # Coded values have a FK to society.  Aggregate the societies from each value
        values = VariableCodedValue.objects.filter(id__in=coded_value_ids)
        values = values.select_related('society','variable')
        for value in values:
            result_set.add_cultural(value.society,value.variable,value)

    if 'environmental_filters' in request.DATA:
        criteria.append(SEARCH_ENVIRONMENTAL)
        environmental_filters = request.DATA['environmental_filters']
        # There can be multiple filters, so we must aggregate the results.
        for filter in environmental_filters:
            values = EnvironmentalValue.objects.filter(variable=filter['id'])
            operator = filter['operator']
            if operator == 'inrange':
                values = values.filter(value__gt=filter['params'][0]).filter(value__lt=filter['params'][1])
            elif operator == 'outrange':
                values = values.filter(value__gt=filter['params'][1]).filter(value__lt=filter['params'][0])
            elif operator == 'gt':
                values = values.filter(value__gt=filter['params'][0])
            elif operator == 'lt':
                values = values.filter(value__lt=filter['params'][0])
            values = values.select_related('variable','environmental__society')
            # get the societies from the values
            for value in values:
                result_set.add_environmental(value.society(), value.variable, value)

    # Filter the results to those that matched all criteria
    result_set.finalize(criteria)
    return Response(SocietyResultSetSerializer(result_set).data)

