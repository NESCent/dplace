from models import *
from rest_framework import viewsets
from serializers import *

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