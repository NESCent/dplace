__author__ = 'dan'
from rest_framework_gis.filterset import GeoFilterSet
from rest_framework_gis.filters import GeometryFilter
from django_filters import CharFilter
from models import GeographicRegion

class GeographicRegionFilter(GeoFilterSet):
    region_nam = CharFilter(name='region_nam', lookup_type='icontains')
    continent = CharFilter(name='continent', lookup_type='icontains')
    contains_geom = GeometryFilter(name='geom', lookup_type='contains')

    class Meta:
        model = GeographicRegion
