import json
import re
import datetime
from itertools import groupby
import logging

from django.db import connection
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect

from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse

from dplace_app.filters import GeographicRegionFilter
from dplace_app.renderers import DPLACECSVRenderer
from dplace_app import serializers
from dplace_app import models
from dplace_app.tree import update_newick


log = logging.getLogger('profile')


class CulturalVariableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalVariableSerializer
    filter_fields = ('label', 'name', 'index_categories', 'niche_categories', 'source')
    queryset = models.CulturalVariable.objects.all().prefetch_related('index_categories', 'niche_categories')

    # Override retrieve to use the detail serializer, which includes categories
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = serializers.CulturalVariableDetailSerializer(self.object)
        return Response(serializer.data)


class CulturalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CulturalCategorySerializer
    filter_fields = ('name', 'index_variables', 'niche_variables')
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
    queryset = models.CulturalValue.objects.select_related('variable', 'code', 'source').all()


class SocietyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SocietySerializer
    queryset = models.Society.objects.all().select_related(
        'source', 'language__iso_code', 'language__family')
    lookup_field = 'ext_id'

    def detail(self, request, society_id):

        # block spider attacks
        if len(request.GET) > 0 and request.path.startswith('/society'):
            raise Http404

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
        if society.hraf_link and '(' in society.hraf_link:
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
    filter_fields = ('variable', 'society',)
    queryset = models.EnvironmentalValue.objects.all()


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageSerializerWithSocieties
    filter_fields = ('name', 'iso_code', 'societies', 'family',)
    queryset = models.Language.objects.all()\
        .select_related('family', 'iso_code')\
        .prefetch_related(Prefetch(
            'societies',
            queryset=models.Society.objects.exclude(culturalvalue__isnull=True)
        ))
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


class LanguageTreeLabelsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LanguageTreeLabelsSerializer
    filter_fields = ('label',)
    queryset = models.LanguageTreeLabels.objects.all()
    pagination_class = LargeResultsSetPagination


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SourceSerializer
    filter_fields = ('author', 'name')
    queryset = models.Source.objects.all()
    

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


def result_set_from_query_dict(query_dict):
    from time import time
    _s = time()
    log.info('enter result_set_from_query_dict')

    result_set = serializers.SocietyResultSet()
    sql_joins, sql_where = [], []
    def id_array(l):
        return '(%s)' % ','.join('%s' % int(i) for i in l)

    if 'l' in query_dict:
        sql_joins.append(('language', 'l', 'l.id = s.language_id'))
        sql_where.append('l.id IN ' + id_array(query_dict['l']))
        for lang in models.Language.objects.filter(id__in=query_dict['l']):
            result_set.languages.add(lang)

    if 'c' in query_dict:
        variables = {
            v.id: v for v in models.CulturalVariable.objects
            .filter(id__in=[int(x.split('-')[0]) for x in query_dict['c']])
            .prefetch_related(Prefetch(
                'codes',
                queryset=models.CulturalCodeDescription.objects
                .filter(id__in=[int(x.split('-')[1]) for x in query_dict['c'] if len(x.split('-')) == 2])))
        }

        for variable, codes in groupby(
            sorted(query_dict['c'], key=lambda c: int(c.split('-')[0])),
            key=lambda x: int(str(x).split('-')[0])
        ):
            variable = variables[variable]
            
            codes = [{
                'id': None if (len(c.split('-')) > 2 or len(c.split('-')) == 1) else int(c.split('-')[1]),
                'min': None if len(c.split('-')) < 3 else float(c.split('-')[1]),
                'max': None if len(c.split('-')) < 3 else float(c.split('-')[2])
            } for c in list(codes)]
            
            alias = 'cv%s' % variable.id
            sql_joins.append((
                "culturalvalue",
                alias,
                "{0}.society_id = s.id AND {0}.variable_id = {1}".format(alias, variable.id)
            ))

            if variable.data_type and variable.data_type == 'Continuous':
                include_NA = not all((c['min'] is not None) for c in codes)
                ors = [
                    "({0}.coded_value_float >= %(min)f AND {0}.coded_value_float <= %(max)f)".format(alias) % c
                    for c in codes if ('min' in c and c['min']  is not None)]
                if include_NA:
                    ors.append("%s.coded_value = 'NA'" % alias)
                sql_where.append("(%s)" % ' OR '.join(ors))
                if not include_NA:
                    sql_where.append("{0}.coded_value != 'NA'".format(alias))
            else:
                assert all('id' in c for c in codes)
                sql_where.append("{0}.code_id IN %s".format(alias) % id_array([x['id'] for x in codes]))
            result_set.variable_descriptions.add(serializers.VariableCode(variable.codes, variable))

    if 'e' in query_dict:
        # There can be multiple filters, so we must aggregate the results.
        for varid, criteria in groupby(
            sorted(query_dict['e'], key=lambda c: c[0]),
            key=lambda x: x[0]
        ):
            alias = 'ev%s' % varid
            sql_joins.append((
                "environmentalvalue",
                alias,
                "{0}.society_id = s.id AND {0}.variable_id = {1}".format(alias, int(varid))))

            for varid, operator, params in criteria:
                params = map(float, params)
                if operator == 'inrange':
                    sql_where.append("{0}.value >= {1:f} AND {0}.value <= {2:f}".format(alias, params[0], params[1]))
                elif operator == 'outrange':
                    sql_where.append("{0}.value >= {1:f} AND {0}.value <= {2:f}".format(alias, params[1], params[0]))
                elif operator == 'gt':
                    sql_where.append("{0}.value >= {1:f}".format(alias, params[0]))
                elif operator == 'lt':
                    sql_where.append("{0}.value <= {1:f}".format(alias, params[0]))

        for variable in models.EnvironmentalVariable.objects.filter(id__in=[x[0] for x in query_dict['e']]):
            result_set.environmental_variables.add(variable)

    if 'p' in query_dict:
        sql_joins.append(('geographicregion', 'r', 'r.id = s.region_id'))
        sql_where.append('r.id IN %s' % id_array(query_dict['p']))
        for region in models.GeographicRegion.objects.filter(id__in=query_dict['p']):
            result_set.geographic_regions.add(region)

    if sql_where:
        cursor = connection.cursor()
        sql = "select distinct s.id from dplace_app_society as s %s where %s" % (
            ' '.join('join dplace_app_%s as %s on %s' % t for t in sql_joins),
            ' AND '.join(sql_where))
        cursor.execute(sql)
        soc_ids = [r[0] for r in cursor.fetchall()]
    else:
        soc_ids = []

    soc_query = models.Society.objects.filter(id__in=soc_ids)\
        .select_related('source', 'language__family', 'language__iso_code', 'region')
    if result_set.geographic_regions:
        soc_query = soc_query.select_related('region')
    if result_set.variable_descriptions:
        soc_query = soc_query.prefetch_related(Prefetch(
            'culturalvalue_set',
            to_attr='selected_cvalues',
            queryset=models.CulturalValue.objects
            # FIXME: this selects possibly too many values, in case there are multiple
            # values for the same variable, not all of them matching the criteria.
            .filter(variable_id__in=[v.variable.id for v in result_set.variable_descriptions])
            .prefetch_related('references')))
    if result_set.environmental_variables:
        soc_query = soc_query.prefetch_related(Prefetch(
            'environmentalvalue_set',
            to_attr='selected_evalues',
            queryset=models.EnvironmentalValue.objects.filter(
                variable_id__in=[v.id for v in result_set.environmental_variables])))

    for i, soc in enumerate(soc_query):
        soc_result = serializers.SocietyResult(soc)
        if result_set.variable_descriptions:
            for cval in soc.selected_cvalues:
                soc_result.variable_coded_values.add(cval)
        if result_set.environmental_variables:
            for eval in soc.selected_evalues:
                soc_result.environmental_values.add(eval)
        result_set.societies.add(soc_result)

    log.info('mid 1: %s' % (time() - _s,))

    # Filter the results to those that matched all criteria
    #result_set.finalize(criteria)
    log.info('mid 2: %s' % (time() - _s,))
    return result_set
    
@api_view(['GET'])
@permission_classes((AllowAny,))
def trees_from_societies(request):
    language_trees = []
    for k, v in request.query_params.lists():
        soc_ids = v
        labels = models.LanguageTreeLabels.objects.filter(societies__id__in=soc_ids).all()
        
        global_tree = None
        global_newick = []
        global_isolates = []

    for t in models.LanguageTree.objects\
            .filter(taxa__societies__id__in=soc_ids)\
            .prefetch_related(
                'taxa__languagetreelabelssequence_set__labels',
                'taxa__languagetreelabelssequence_set__society',
            )\
            .distinct():
            
            if 'global' in t.name:
                global_tree = t
                # TODO ask @Bibiko once the isolates are in the db under global.tree as string: isol1,isol2,isol3,...
                # global_isolates.extend(t.newick_string.split(','))
                global_isolates.extend(['alse1251','amas1236','bana1292','calu1239','chim1301','chit1248','chon1248','coah1252','coos1249','furr1244','gaga1251','guai1237','guat1253','hadz1240','high1242','kara1289','karo1304','klam1254','kute1249','lara1258','mull1237','natc1249','nort2938','paez1247','pume1238','pura1257','pure1242','sali1253','sand1273','seri1257','shom1245','sius1254','sout1439','take1257','ticu1245','timu1245','tiwi1244','toll1241','trum1247','uruu1244','wara1303','wash1253','yama1264','yuch1247','zuni1245'])
            else:
                if update_newick(t, labels):
                    language_trees.append(t)
                    if 'glotto' in t.name:
                        #remove last ; in order to be able to join the trees
                        global_newick.append(t.newick_string[:-1])
        
    if global_tree:
        langs_in_tree = [str(l.label) for l in labels]
        #add isolates if present in current selection
        [global_newick.append('(' + isolate + ':1)') for isolate in global_isolates if isolate in langs_in_tree]
        #join all pruned glottolog trees into the global one
        global_tree.newick_string = '(' + ','.join(global_newick) + ');'
        language_trees.append(global_tree)
            
    return Response(serializers.LanguageTreeSerializer(language_trees, many=True).data)


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
    from time import time
    from django.db import connection
    s = time()
    log.info('%s find_societies 1: %s queries' % (time() - s, len(connection.queries)))
    query = {}
    if 'name' in request.query_params:
        result_set = serializers.SocietyResultSet()
        q = request.query_params['name']
        if q:
            soc = models.Society.objects.filter(
                Q(name__icontains=q) | Q(alternate_names__unaccent__icontains=q))
            for s in soc:
                if s.culturalvalue_set.count():
                    result_set.societies.add(serializers.SocietyResult(s))
        return Response(serializers.SocietyResultSetSerializer(result_set).data)

    for k, v in request.query_params.lists():
        if str(k) == 'c':
            query[k] = v
        else:
            query[k] = [json.loads(vv) for vv in v]
    result_set = result_set_from_query_dict(query)
    log.info('%s find_societies 2: %s queries' % (time() - s, len(connection.queries)))
    d = serializers.SocietyResultSetSerializer(result_set).data
    log.info('%s find_societies 3: %s queries' % (time() - s, len(connection.queries)))
    for i, q in enumerate(
            sorted(connection.queries, key=lambda q: q['time'], reverse=True)):
        if i < 5:  # pragma: no cover
            log.info('%s for %s' % (q['time'], q['sql'][:200]))
    return Response(d)


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

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((DPLACECSVRenderer,))
def csv_download(request):
    query_dict = get_query_from_json(request)
    result_set = result_set_from_query_dict(query_dict)
    response = Response(serializers.SocietyResultSetSerializer(result_set).data)
    filename = "dplace-societies-%s.csv" % datetime.datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response

