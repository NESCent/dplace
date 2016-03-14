import json
import re
import datetime
from itertools import groupby

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from ete2 import Tree
from ete2.coretype.tree import TreeError
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import Response
from rest_framework.renderers import JSONRenderer

from dplace_app.filters import GeographicRegionFilter
from dplace_app.renderers import DPLACECSVRenderer, ZipRenderer
from dplace_app import serializers
from dplace_app import models


class CulturalVariableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalVariableSerializer
    filter_fields = ('label', 'name', 'index_categories', 'niche_categories', 'source')
    queryset = models.CulturalVariable.objects.all()

    # Override retrieve to use the detail serializer, which includes categories
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = serializers.CulturalVariableDetailSerializer(self.object)
        return Response(serializer.data)


class CulturalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalCategorySerializer
    filter_fields = ('name', 'index_variables', 'niche_variables',)
    queryset = models.CulturalCategory.objects.all()
    # Override retrieve to use the detail serializer, which includes variables

    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = serializers.CulturalCategoryDetailSerializer(self.object)
        return Response(serializer.data)


class CulturalCodeDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalCodeDescriptionSerializer
    filter_fields = ('variable',)
    queryset = models.CulturalCodeDescription.objects.all()


class CulturalValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalValueSerializer
    filter_fields = ('variable', 'coded_value', 'code', 'society',)
    # Avoid additional database trips by select_related for foreign keys
    queryset = models.CulturalValue.objects.select_related('variable', 'code').all()


class SocietyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SocietySerializer
    queryset = models.Society.objects.all().select_related(
        'source', 'language__iso_code', 'language__family')
    lookup_field = 'ext_id'

    def detail(self, request, society_id):
        society = get_object_or_404(models.Society, ext_id=society_id)
        # gets the society's location for inset map
        location = {}
        if society.location:
            location = {
                'lat': society.location['coordinates'][1],
                'lng': society.location['coordinates'][0]
            }

        # gets other societies in database with the same xd_id
        xd_id = models.Society.objects.filter(
            xd_id=society.xd_id).exclude(ext_id=society_id)
        if '(' in society.hraf_link:
            hraf_link = society.hraf_link.split('(')[len(society.hraf_link.split('('))-1]
        else:
            hraf_link = ''
        environmentals = society.get_environmental_data()
        cultural_traits = society.get_cultural_trait_data()
        references = society.get_data_references()
        language_classification = None
        
        if society.language:
            # just glottolog at the moment
            language_classification = models.LanguageFamily.objects\
                .filter(name=society.language.family.name, scheme='G')

        return Response(
            {
                'society': society,
                'hraf_link': hraf_link[0:len(hraf_link)-1],
                'xd_id': xd_id,
                'location': location,
                'language_classification': language_classification,
                'environmentals': dict(environmentals),
                'cultural_traits': dict(cultural_traits),
                'references': references
            },
            template_name='society.html'
        )


class ISOCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ISOCodeSerializer
    filter_fields = ('iso_code',)
    queryset = models.ISOCode.objects.all()


class EnvironmentalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.EnvironmentalCategorySerializer
    filter_fields = ('name',)
    queryset = models.EnvironmentalCategory.objects.all()


class EnvironmentalVariableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.EnvironmentalVariableSerializer
    filter_fields = ('name', 'category', 'units',)
    queryset = models.EnvironmentalVariable.objects.all()


class EnvironmentalValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.EnvironmentalValueSerializer
    filter_fields = ('variable', 'environmental',)
    queryset = models.EnvironmentalValue.objects.all()


class EnvironmentalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.EnvironmentalSerializer
    filter_fields = ('society', 'iso_code',)
    queryset = models.Environmental.objects.all()


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageSerializer
    filter_fields = ('name', 'iso_code', 'societies', 'family',)
    queryset = models.Language.objects.all()
    pagination_class = LargeResultsSetPagination


class LanguageFamilyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageFamilySerializer
    filter_fields = ('name', 'scheme',)
    queryset = models.LanguageFamily.objects.all().order_by('name')
    pagination_class = LargeResultsSetPagination


class TreeResultsSetPagination(PageNumberPagination):
    """
    Since trees may have *many* languages, which are serialized as well, we limit the
    page size to just 1.
    """
    page_size = 1
    page_size_query_param = 'page_size'
    max_page_size = 10


class LanguageTreeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageTreeSerializer
    filter_fields = ('name',)
    queryset = models.LanguageTree.objects.all()
    pagination_class = TreeResultsSetPagination


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SourceSerializer
    filter_fields = ('author', 'name')
    queryset = models.Source.objects.all()


# maybe needs cleaning up in the future
def trees_from_languages_array(language_ids):
    """
    Takes a list of language ids
    
    Returns trees that contain the societies from the SocietyResultSet
    """
    trees = models.LanguageTree.objects\
        .filter(languages__pk__in=language_ids)\
        .prefetch_related('languages__family', 'languages__iso_code')\
        .distinct()
    for t in trees:
        if 'glotto' in t.name:
            langs_in_tree = [
                str(l.glotto_code) for l in t.languages.all() if l.id in language_ids
            ]
        else:
            langs_in_tree = [
                str(l.iso_code.iso_code)
                for l in t.languages.all() if l.id in language_ids
            ]
        newick = Tree(t.newick_string, format=1)
        try:
            if 'glotto' not in t.name:
                newick.prune(langs_in_tree, preserve_branch_length=True)
                t.newick_string = newick.write(format=1)
            else:
                # kind of hacky, but needed for when langs_in_tree is only 1
                # in future, maybe exclude these trees from the search results?
                if len(langs_in_tree) == 1:
                    node = newick.search_nodes(name=langs_in_tree[0])
                    if len(node[0].get_leaves()) > 1:
                        t.newick_string = "(%s:1);" % (langs_in_tree[0])
                    elif (len(node[0].get_leaves()) == 1) \
                            and not (node[0].get_leaves()[0].name == langs_in_tree[0]):
                        t.newick_string = "(%s:1);" % (langs_in_tree[0])
                    else:
                        newick.prune(langs_in_tree, preserve_branch_length=True)
                        t.newick_string = newick.write(format=1)
                else:
                    newick.prune(langs_in_tree, preserve_branch_length=True)
                    t.newick_string = newick.write(format=1)
        except TreeError:
            continue
    return trees


def result_set_from_query_dict(query_dict):
    result_set = serializers.SocietyResultSet()
    # Criteria keeps track of what types of data were searched on, so that we can
    # AND them together
    criteria = []

    if 'l' in query_dict:
        criteria.append(serializers.SEARCH_LANGUAGE)
        for society in models.Society.objects\
                .filter(language_id__in=query_dict['l'])\
                .select_related(
                    'source',
                    'language__family',
                    'language__iso_code'):
            if society.culturalvalue_set.count():
                result_set.add_language(society, society.language)

    if 'c' in query_dict:
        criteria.append(serializers.SEARCH_VARIABLES)

        variables = {
            v.id: v for v in models.CulturalVariable.objects
            .filter(id__in=[x['variable'] for x in query_dict['c']])
            .prefetch_related(Prefetch(
                'codes',
                queryset=models.CulturalCodeDescription.objects
                .filter(id__in=[x.get('id') for x in query_dict['c']])))
        }

        for variable, codes in groupby(
            sorted(query_dict['c'], key=lambda c: c['variable']),
            key=lambda x: x['variable']
        ):
            variable = variables[variable]
            codes = list(codes)

            if variable.data_type and variable.data_type == 'Continuous':
                assert all('min' in c for c in codes)
                query = reduce(
                    lambda q, x: q | Q(
                        coded_value_float__gt=x['min'], coded_value_float__lt=x['max']),
                    codes,
                    Q(id=0))
                values = models.CulturalValue.objects\
                    .filter(variable=variable)\
                    .filter(query)\
                    .exclude(coded_value='NA')
            else:
                assert all('id' in c for c in codes)
                values = models.CulturalValue.objects \
                    .filter(code_id__in=[x['id'] for x in codes])

            for value in values\
                    .select_related('society__language__family') \
                    .select_related('society__language__iso_code')\
                    .select_related('society__source')\
                    .prefetch_related('references'):
                result_set.add_cultural(value.society, variable, variable.codes, value)

    if 'e' in query_dict:
        criteria.append(serializers.SEARCH_ENVIRONMENTAL)
        # There can be multiple filters, so we must aggregate the results.
        for varid, operator, params in query_dict['e']:
            values = models.EnvironmentalValue.objects.filter(variable_id=varid)
            if operator == 'inrange':
                values = values.filter(value__gt=params[0]).filter(value__lt=params[1])
            elif operator == 'outrange':
                values = values.filter(value__gt=params[1]).filter(value__lt=params[0])
            elif operator == 'gt':
                values = values.filter(value__gt=params[0])
            elif operator == 'lt':
                values = values.filter(value__lt=params[0])
            values = values.select_related(
                'variable', 'environmental__society__language')
            # get the societies from the values
            for value in values:
                result_set.add_environmental(value.society(), value.variable, value)

    if 'p' in query_dict:
        criteria.append(serializers.SEARCH_GEOGRAPHIC)
        for society in models.Society.objects\
                .filter(region_id__in=query_dict['p'])\
                .select_related(
                    'region',
                    'language__family',
                    'language__iso_code')\
                .prefetch_related('source').all():
            result_set.add_geographic_region(society, society.region)
    # Filter the results to those that matched all criteria
    result_set.finalize(criteria)

    # search for language trees
    language_ids = []
    for s in result_set.societies:
        if s.society.language:
            language_ids.append(s.society.language.id)
    trees = trees_from_languages_array(language_ids)
    for t in trees:
        result_set.add_language_tree(t)

    return result_set


@api_view(['GET'])
@permission_classes((AllowAny,))
def find_societies(request):
    """
    View to find the societies that match an input request.  Currently expects
    { language_filters: [{language_ids: [1,2,3]}], variable_codes: [4,5,6...],
    environmental_filters: [{id: 1, operator: 'gt', params: [0.0]},
    {id:3, operator 'inrange', params: [10.0,20.0] }] }

    Returns serialized collection of SocietyResult objects
    """
    query = {}
    for k, v in request.query_params.lists():
        query[k] = [json.loads(vv) for vv in v]
    result_set = result_set_from_query_dict(query)
    d = serializers.SocietyResultSetSerializer(result_set).data
    return Response(d)


def get_query_from_json(request):
    query_string = request.query_params.get('query')
    if query_string is None:
        raise Http404('missing query parameter')
    try:
        query_dict = json.loads(query_string)
    except ValueError:
        raise Http404('malformed query parameter')
    if not isinstance(query_dict, dict):
        raise Http404('malformed query parameter')
    return query_dict


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_categories(request):
    """
    Filters categories for sources, as some categories are empty for some sources
    """
    query_dict = get_query_from_json(request)
    categories = models.CulturalCategory.objects.all()
    source_categories = []
    if 'source' in query_dict:
        source = models.Source.objects.filter(id=query_dict['source'])
        variables = models.CulturalVariable.objects.filter(source=source)
        for c in categories:
            if variables.filter(index_categories=c.id):
                source_categories.append(c)
        return Response(
            serializers.CulturalCategorySerializer(source_categories, many=True).data)
    return Response(serializers.CulturalCategorySerializer(categories, many=True).data)


@api_view(['GET'])
@permission_classes((AllowAny,))
def get_dataset_sources(request):
    return Response(
        serializers.SourceSerializer(
            models.Source.objects.all().exclude(name=""), many=True).data)


class GeographicRegionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.GeographicRegionSerializer
    model = models.GeographicRegion
    filter_class = GeographicRegionFilter
    queryset = models.GeographicRegion.objects.all()


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_min_and_max(request):
    res = {}
    environmental_id = get_query_from_json(request).get('environmental_id')
    if environmental_id:
        values = models.EnvironmentalValue.objects.filter(variable__id=environmental_id)
        min_value = None
        max_value = 0
        for v in values:
            if min_value is None:
                min_value = v.value

            if v.value < min_value:
                min_value = v.value
            elif v.value > max_value:
                max_value = v.value
        res = {'min': format(min_value or 0.0, '.4f'), 'max': format(max_value, '.4f')}
    return Response(res)


@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def bin_cont_data(request):  # MAKE THIS GENERIC
    bf_id = get_query_from_json(request).get('bf_id')
    bins = []
    if bf_id:
        values = models.CulturalValue.objects.filter(variable__id=bf_id)
        min_value = None
        max_value = 0.0
        missing_data_option = False
        for v in values:
            if re.search('[a-zA-Z]', v.coded_value):
                if not missing_data_option:
                    bins.append({
                        'code': v.coded_value,
                        'description': v.code.description,
                        'variable': bf_id,
                    })
                    missing_data_option = True
                continue
            else:
                v.coded_value = v.coded_value.replace(',', '')
                if min_value is None:
                    min_value = float(v.coded_value)
                elif float(v.coded_value) < min_value:
                    min_value = float(v.coded_value)
                elif float(v.coded_value) > max_value:
                    max_value = float(v.coded_value)

        min_value = min_value or 0.0  # This is the case when there are no values!
        data_range = max_value - min_value
        bin_size = data_range / 5
        min_bin = min_value
        for x in range(0, 5):
            min = min_bin
            max = min_bin + bin_size
            bins.append({
                'code': x,
                'description': str(min) + ' - ' + str(max),
                'min': min_bin,
                'max': min_bin + bin_size,
                'variable': bf_id,
            })
            min_bin = min_bin + bin_size + 1
    return Response(bins)


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((DPLACECSVRenderer,))
def csv_download(request):
    result_set = result_set_from_query_dict(request.data)
    response = Response(serializers.SocietyResultSetSerializer(result_set).data)
    filename = "dplace-societies-%s.csv" % datetime.datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response


@api_view(['POST'])
@permission_classes((AllowAny,))
@renderer_classes((ZipRenderer,))
def zip_legends(request):
    # query_string = request.QUERY_PARAMS['query']
    result_set = request.data  # json.loads(query_string)
    to_download = serializers.ZipResultSet()
    if 'name' in result_set:
        to_download.name = str(result_set['name'])
    if 'tree' in result_set:
        to_download.tree = str(result_set['tree'])
    if 'legends' in result_set:
        for l in result_set['legends']:
            legend = serializers.Legend(l['name'], l['svg'])
            to_download.legends.append(legend)
    response = Response(serializers.ZipResultSetSerializer(to_download).data)
    filename = "dplace-trees-%s.zip" % datetime.datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response
