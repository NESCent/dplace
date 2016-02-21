from django.http import Http404
from django.shortcuts import render, get_object_or_404
from dplace_app.models import Society, Language, LanguageFamily


def view_language(request, language_id):
    language = get_object_or_404(Language, pk=language_id)
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
    return render(request, 'angular.html', dict())
