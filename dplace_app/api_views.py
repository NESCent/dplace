from models import *
from rest_framework import viewsets
from serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.views import Request, Response
from rest_framework.parsers import JSONParser
from itertools import chain

# Resource routes
class EAVariableDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EAVariableDescriptionSerializer
    filter_fields = ('number', 'name',)
    queryset = EAVariableDescription.objects.all()

class EAVariableCodeDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EAVariableCodeDescriptionSerializer
    filter_fields = ('variable', 'code', 'description',)
    queryset = EAVariableCodeDescription.objects.all()

# Can filter by code, code__variable, or society
class EAVariableCodedValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EAVariableCodedValueSerializer
    filter_fields = ('variable','coded_value','code','society','code',)
    # Avoid additional database trips by select_related for foreign keys
    queryset = EAVariableCodedValue.objects.select_related('variable').select_related('code').all()

class SocietyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocietySerializer
    queryset = Society.objects.all()

class ISOCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ISOCodeSerializer
    filter_fields = ('iso_code',)
    queryset = ISOCode.objects.all()

class EnvironmentalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalSerializer
    filter_fields = ('society', 'iso_code',)
    queryset = Environmental.objects.all()

class LanguageClassViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageClassSerializer
    filter_fields = ('level', 'parent', 'name',)
    model = LanguageClass
    def get_queryset(self):
        queryset = LanguageClass.objects.all()
        level = self.request.QUERY_PARAMS.get('level', None)
        if level is not None:
            queryset = queryset.filter(level=level)
        else:
            queryset = queryset.filter(level=1)
        return queryset

class LanguageFamilyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageFamilySerializer
    filter_fields = ('name',)
    queryset = LanguageFamily.objects.all()

# Need an API to get classifications / languages for a class

class LanguageClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageClassificationSerializer
    filter_fields = ('scheme', 'language', 'name', 'family', 'class_family', 'class_subfamily', 'class_subsubfamily',)
    queryset = LanguageClassification.objects.all()

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageSerializer
    filter_fields = ('name', 'iso_code', 'society',)
    queryset = Language.objects.all()

# search/filter APIs
@api_view(['GET'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def find_societies(request):
    """
    View to find the societies that match an input request.  Currently expects
    { language_class_ids: [1,2,3...], ea_variable_codes: [4,5,6...] }
    """
    results = {'language_societies': None, 'ea_variable_societies': None}

    language_class_ids = request.QUERY_PARAMS.getlist('language_class_ids')
    if len(language_class_ids) > 0:
        language_class_ids = [int(x) for x in language_class_ids]
        # Loop over the language class IDs to get classes
        language_classes = LanguageClass.objects.filter(pk__in=language_class_ids)
        # Classifications are related to classes
        language_classifications = []
        for language_class in language_classes:
            language_classifications += language_class.languages1.all()
            language_classifications += language_class.languages2.all()
            language_classifications += language_class.languages3.all()
        # Now get languages from classifications
        iso_codes = []
        for language_classification in language_classifications:
            iso_codes.append(language_classification.language.iso_code)
        # now get societies from ISO codes
        results['language_societies'] = Society.objects.filter(iso_code__in=iso_codes)

    ea_variable_code_ids = request.QUERY_PARAMS.getlist('ea_variable_codes')
    if len(ea_variable_code_ids) > 0:
        # Now get the societies from EA Variables
        ea_variable_code_ids = [int(x) for x in ea_variable_code_ids]
        codes = EAVariableCodeDescription.objects.filter(pk__in=ea_variable_code_ids) # returns a queryset
        coded_value_ids = []
        # Aggregate all the coded values for each selected code
        for code in codes:
            coded_value_ids += code.eavariablecodedvalue_set.values_list('id', flat=True)
        # Coded values have a FK to society.  Aggregate the societies from each value
        results['ea_variable_societies'] = Society.objects.filter(eavariablecodedvalue__in=coded_value_ids)

    societies = None
    # Intersect the querysets
    for k in results.keys():
        if results[k] is not None:
            if societies is None:
                societies = results[k]
            else:
                societies = societies & results[k]

    return Response(SocietySerializer(societies).data)


