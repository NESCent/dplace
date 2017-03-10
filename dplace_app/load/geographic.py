from dplace_app.models import GeographicRegion


def load_regions(geojson):
    regions = [r['properties'] for r in geojson['features']]
    GeographicRegion.objects.bulk_create([
        GeographicRegion(**{k.lower(): v for k, v in r.items()}) for r in regions])
    return len(regions)
