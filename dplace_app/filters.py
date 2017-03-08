from rest_framework_gis.filterset import GeoFilterSet
from rest_framework_gis.filters import GeometryFilter
import django_filters

from dplace_app.models import GeographicRegion


class GeographicRegionFilter(GeoFilterSet):
    region_nam = django_filters.CharFilter(name='region_nam', lookup_expr=['icontains'])
    continent = django_filters.CharFilter(name='continent', lookup_expr=['icontains'])
    contains_geom = GeometryFilter(name='geom', lookup_expr=['contains'])

    class Meta:
        model = GeographicRegion
        fields = '__all__'
