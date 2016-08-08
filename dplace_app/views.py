from django.http import Http404
from django.shortcuts import render, get_object_or_404
from dplace_app.models import Language


def view_language(request, glottocode):
    language = get_object_or_404(Language, glottocode=glottocode)
    if language.society is None:
        raise Http404
    environmentals = language.society.environmentals.all()
    ea_values = language.society.get_ethnographic_atlas_data()
    return render(request, 'society.html', {
        'language': language,
        'society': language.society,
        'environmentals': environmentals,
        'ea_values': ea_values
    })


def angular(request):

    # block spider attacks
    if len(request.GET) > 0 and request.path.startswith('/home'):
        raise Http404

    return render(request, 'angular.html', dict())
