from rest_framework_gis.filterset import GeoFilterSet
from rest_framework_gis.filters import GeometryFilter
import django_filters

from models import GeographicRegion


class GeographicRegionFilter(GeoFilterSet):
    region_nam = django_filters.CharFilter(name='region_nam', lookup_type='icontains')
    continent = django_filters.CharFilter(name='continent', lookup_type='icontains')
    contains_geom = GeometryFilter(name='geom', lookup_type='contains')

    class Meta:
        model = GeographicRegion
