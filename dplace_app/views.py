from __builtin__ import dict
from django.shortcuts import render, get_object_or_404
from dplace_app.models import Society
from forms import GeoForm
from models import ISOCode
# Create your views here.

def search_geo(request):
    if request.method == 'POST':
        # handle search
        form = GeoForm(request.POST)
        results = []
        region = None
        if form.is_valid():
            cd = form.cleaned_data
            region = cd['region'] # Polygon
            isocodes = ISOCode.objects.filter(location__intersects=region)
            # get the environmentals
            for isocode in isocodes:
                result = {
                'isocode': isocode.iso_code,
                'environmentals': isocode.environmentals.all(),
                'societies':isocode.societies.all(),}
                results.append(result)
        return render(request, 'search_geo.html', {'form': form, 'region': region, 'results': results})
    else:
        form = GeoForm()
        return render(request, 'search_geo.html', {'form': form})

def view_society(request, society_id):
    society = get_object_or_404(Society, pk=society_id)
    environmentals = society.environmentals.all()
    ea_values = society.get_ethnographic_atlas_data()
    return render(request,'society.html', {'society': society,
                                           'environmentals': environmentals,
                                           'ea_values': ea_values})

def angular(request):
    return render(request, 'angular.html', dict())
