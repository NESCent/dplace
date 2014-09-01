from dplace_app.models import Source

_SOURCE_CACHE = {}
def get_source(source='EA'):
    if source in _SOURCE_CACHE:
        return _SOURCE_CACHE[source]
    
    if source == 'EA':
        try:
            o = Source.objects.get(year="1999", author="Murdock et al.")
        except Source.DoesNotExist:
            o = Source.objects.create(
                year="1999",
                author="Murdock et al.",
                reference="Murdock, G. P., R. Textor, H. Barry, III, D. R. White, J. P. Gray, and W. T. Divale. 1999. Ethnographic Atlas. World Cultures 10:24-136 (codebook)",
                focal_year='',
                subcase='',
            )
    elif source == 'Binford':
        try:
            o = Source.objects.get(year="2001", author="Binford")
        except Source.DoesNotExist:
            o = Source.objects.create(
                year="2001",
                author="Binford",
                reference="Binford, L. 2001. Constructing Frames of Reference: An Analytical Method for Archaeological Theory Building Using Hunter-gatherer and Environmental Data Sets. University of California Press",
                focal_year='',
                subcase='',
            )
    else:
        raise ValueError("Unknown Source: %s" % source)
    _SOURCE_CACHE[source] = o
    return o