from models import *
from rest_framework import viewsets
from serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.views import Request, Response
from rest_framework.parsers import JSONParser

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
class EAVariableValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EAVariableValueSerializer
    # TODO: change code__variable to just variable and make it more user-friendly
    filter_fields = ('code__variable', 'code', 'society')
    # Avoid additional database trips by select_related for foreign keys
    queryset = EAVariableValue.objects.select_related('code').select_related('code__variable').all()

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
    filter_fields = ('level', 'parent', 'name')
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
    filter_fields = ('name')
    queryset = LanguageFamily.objects.all()

# Need an API to get classifications / languages for a class

class LanguageClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageClassificationSerializer
    filter_fields = ('scheme', 'language', 'name', 'family', 'class_family', 'class_subfamily', 'class_subsubfamily')
    queryset = LanguageClassification.objects.all()

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageSerializer
    filter_fields = ('name', 'iso_code__isocode', 'society__ext_id')
    queryset = Language.objects.all()

# search/filter APIs
@api_view(['GET','POST'])
@permission_classes((IsAuthenticatedOrReadOnly,))
def find_societies(request):
    """
    View to find the societies that match an input request.  Currently expects
    { language_class_ids: [1,2,3...] }
    """
    data = JSONParser.parse(request.DATA)
    language_class_ids = data['language_class_ids']
    print "language class ids: %s" % ",".join(language_class_ids)
    # Loop over the language class IDs to get classes
    language_classes = LanguageClass.objects.filter(pk__in=language_class_ids)
    # Classifications are related to classes
    language_classifications = []
    for language_class in language_classes:
        language_classifications.append(language_class.languages1)
        language_classifications.append(language_class.languages2)
        language_classifications.append(language_class.languages3)
    # Now get languages from classifications
    for language_classification in language_classifications:
        iso_codes.append(language.iso_code)
    # now get societies from ISO codes
    societies = Society.objects.filter(iso_code__in=iso_codes)
    return Response({"societies": SocietySerializer(societies)})


