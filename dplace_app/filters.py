__author__ = 'dan'
from rest_framework_gis.filterset import GeoFilterSet
from rest_framework_gis.filters import GeometryFilter
import django_filters

from models import *

class GeographicRegionFilter(GeoFilterSet):
    region_nam = django_filters.CharFilter(name='region_nam', lookup_type='icontains')
    continent = django_filters.CharFilter(name='continent', lookup_type='icontains')
    contains_geom = GeometryFilter(name='geom', lookup_type='contains')

    class Meta:
        model = GeographicRegion

class VariableCodeDescriptionFilter(django_filters.FilterSet):
    class Meta:
        model = VariableCodeDescription
        fields = ['variable', 'code', 'description']

class LanguageClassificationFilter(django_filters.FilterSet):
    class Meta:
        model = LanguageClassification
        fields = ['scheme', 'language', 'class_family', 'class_subfamily', 'class_subsubfamily']

class LanguageClassFilter(django_filters.FilterSet):
    class Meta:
        model = LanguageClass
        fields = ['level', 'parent', 'name']
