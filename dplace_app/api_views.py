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
