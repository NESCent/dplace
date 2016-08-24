from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from dplace_app.models import Language
from django.views.decorators.csrf import ensure_csrf_cookie
from six import StringIO
import csv, json, zipfile, datetime, sys

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

def download_file(request):
    if request.method =='POST':
        s = StringIO()
        zf = zipfile.ZipFile(s, "w")
        try:
            if 'values' in request.POST:
                result_set = json.loads(request.POST.get('values'))
            else:
                result_set = {}
            name = 'tree.svg'
            tree = ''
            if 'n' in result_set:
                name = result_set['n'][0]
            if 't' in result_set:
                tree = result_set['t'][0]
            zf.writestr(
                name.encode('utf-8'),
                tree.encode('utf-8')
            )
                
            if 'l' in result_set:
                for l in result_set['l']:
                    zf.writestr(
                        l['name'].encode('utf-8'),
                        l['svg'].encode('utf-8')
                    )
        finally:
            zf.close()
        
    filename = "dplace-trees-%s.zip" % datetime.datetime.now().strftime("%Y-%m-%d")
    response = HttpResponse(s.getvalue(), content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename='+filename
    return response

@ensure_csrf_cookie
def angular(request):

    # block spider attacks
    if len(request.GET) > 0 and request.path.startswith('/home'):
        raise Http404

    return render(request, 'angular.html', dict())
