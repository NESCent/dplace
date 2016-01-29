from dplace_app.models import GeographicRegion
from django.contrib.gis.utils import LayerMapping

# Auto-generated `LayerMapping` dictionary for GeographicRegion model
# via manage.py ogrinspect level2.shp GeographicRegion --srid=4326 --mapping --multi

geographicregion_mapping = {
    'level_2_re': 'LEVEL_2_RE',
    'count': 'COUNT',
    'region_nam': 'REGION_NAM',
    'continent': 'CONTINENT',
    'tdwg_code': 'TDWG_CODE',
    'geom': 'MULTIPOLYGON',
}


def load_regions(shapefile=None, verbose=False):
    lm = LayerMapping(GeographicRegion, shapefile, geographicregion_mapping,
                      transform=False, encoding='iso-8859-1')
    lm.save(strict=True, verbose=verbose)
