from __builtin__ import dict
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from dplace_app.models import Society, Language, LanguageClassification

def view_society(request, society_id):
    society = get_object_or_404(Society, pk=society_id)
    xd_id = Society.objects.filter(xd_id=society.xd_id).exclude(pk=society_id) #gets other societies in database with the same xd_id
    environmentals = society.get_environmental_data()
    cultural_traits = society.get_cultural_trait_data()
    references = society.get_data_references()
    if society.language:
        language_classification = LanguageClassification.objects.filter(language=society.language, scheme='G') #just glottolog at the moment
    return render(request,'society.html', {'society': society,
                                            'xd_id': xd_id,
                                            'language_classification':language_classification,
                                           'environmentals': dict(environmentals),
                                           'cultural_traits': dict(cultural_traits),
                                           'references': references,})

def view_language(request, language_id):
    language = get_object_or_404(Language, pk=language_id)
    if language.society is None:
        raise Http404
    environmentals = language.society.environmentals.all()
    ea_values = language.society.get_ethnographic_atlas_data()
    return render(request,'society.html', {'language': language,
                                           'society': language.society,
                                           'environmentals': environmentals,
                                           'ea_values': ea_values})

def angular(request):
    return render(request, 'angular.html', dict())
