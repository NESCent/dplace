import json

from dplace_app.models import GeographicRegion

from dplace_app.load.util import delete_all


def load_regions(geojson):
    delete_all(GeographicRegion)

    with open(geojson) as fp:
        regions = json.load(fp)['features']

    GeographicRegion.objects.bulk_create([
        GeographicRegion(**{k.lower(): v for k, v in region['properties'].items()})
        for region in regions])
    return len(regions)
