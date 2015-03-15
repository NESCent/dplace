import json
import re
from django.core.exceptions import ObjectDoesNotExist
from nexus import NexusReader
from rest_framework import viewsets
from serializers import *
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.permissions import *
from rest_framework.views import Request, Response
from rest_framework.renderers import JSONRenderer
from filters import *
from renderers import DPLACECsvRenderer

# Resource routes
class VariableDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableDescriptionSerializer
    filter_fields = ('label', 'name', 'index_categories', 'niche_categories',)
    queryset = VariableDescription.objects.all()
    # Override retrieve to use the detail serializer, which includes categories
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = VariableDescriptionDetailSerializer(self.object)
        return Response(serializer.data)

class VariableCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableCategorySerializer
    filter_fields = ('name', 'index_variables', 'niche_variables',)
    queryset = VariableCategory.objects.all()
    # Override retrieve to use the detail serializer, which includes variables
    def retrieve(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = VariableCategoryDetailSerializer(self.object)
        return Response(serializer.data)

class VariableCodeDescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    # Model ordering is ignored when filter_fields enabled, requires FilterSet subclass
    # see https://github.com/tomchristie/django-rest-framework/issues/1432
    serializer_class = VariableCodeDescriptionSerializer
    filter_class = VariableCodeDescriptionFilter
    queryset = VariableCodeDescription.objects.all()

# Can filter by code, code__variable, or society
class VariableCodedValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = VariableCodedValueSerializer
    filter_fields = ('variable','coded_value','code','society',)
    # Avoid additional database trips by select_related for foreign keys
    queryset = VariableCodedValue.objects.select_related('variable').select_related('code').all()

class SocietyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SocietySerializer
    queryset = Society.objects.all()

class ISOCodeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ISOCodeSerializer
    filter_fields = ('iso_code',)
    queryset = ISOCode.objects.all()
    
class EnvironmentalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalCategorySerializer
    filter_fields = ('name',)
    queryset = EnvironmentalCategory.objects.all()

class EnvironmentalVariableViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalVariableSerializer
    filter_fields = ('name', 'category', 'units',)
    queryset = EnvironmentalVariable.objects.all()

class EnvironmentalValueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalValueSerializer
    filter_fields = ('variable','environmental',)
    queryset = EnvironmentalValue.objects.all()

class EnvironmentalViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnvironmentalSerializer
    filter_fields = ('society', 'iso_code',)
    queryset = Environmental.objects.all()

class LanguageClassViewSet(viewsets.ReadOnlyModelViewSet):
    # Model ordering is ignored when filter_fields enabled, requires FilterSet subclass
    # see https://github.com/tomchristie/django-rest-framework/issues/1432
    serializer_class = LanguageClassSerializer
    filter_class = LanguageClassFilter
    queryset = LanguageClass.objects.all()

# Need an API to get classifications / languages for a class

class LanguageClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    # Model ordering is ignored when filter_fields enabled, requires FilterSet subclass
    # see https://github.com/tomchristie/django-rest-framework/issues/1432
    serializer_class = LanguageClassificationSerializer
    filter_class = LanguageClassificationFilter
    queryset = LanguageClassification.objects.all()

class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageSerializer
    filter_fields = ('name', 'iso_code', 'societies',)
    queryset = Language.objects.all()

class LanguageTreeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LanguageTreeSerializer
    filter_fields = ('name',)
    queryset = LanguageTree.objects.all()
    
def result_set_from_query_dict(query_dict):
    result_set = SocietyResultSet()
    # Criteria keeps track of what types of data were searched on, so that we can
    # AND them together
    criteria = []

    if 'language_classifications' in query_dict:
        criteria.append(SEARCH_LANGUAGE)
        classifications = query_dict['language_classifications']
        for classification in classifications:
            language_ids = [int(classification['language']['id'])]
            languages = Language.objects.filter(pk__in=language_ids) # Returns a queryset
            languages.select_related('societies')
            for language in languages:
                for society in language.societies.all():
                    result_set.add_language(society,language)

    if 'variable_codes' in query_dict:
        criteria.append(SEARCH_VARIABLES)
        f = open('var_codes.txt', 'w')
        for x in query_dict['variable_codes']:
            if 'bf_id' in x:
                min = x['min']
                max = x['max']
                values = VariableCodedValue.objects.filter(variable__id=x['bf_id'])
                values.filter(coded_value__gt=min).filter(coded_value__lt=max)
                values.select_related('society', 'variable')
            else:
                variable_code_ids = [int(x['id']) for x in query_dict['variable_codes']]
                codes = VariableCodeDescription.objects.filter(pk__in=variable_code_ids) # returns a queryset
                coded_value_ids = []
                # Aggregate all the coded values for each selected code
                for code in codes:
                    coded_value_ids += code.variablecodedvalue_set.values_list('id', flat=True)
                # Coded values have a FK to society.  Aggregate the societies from each value
                values = VariableCodedValue.objects.filter(id__in=coded_value_ids)
                values = values.select_related('society','variable')
                
            for value in values:
                result_set.add_cultural(value.society, value.variable, value)
        
        # Now get the societies from variables
       # try:
       #     variable_code_ids = [int(x['id']) for x in query_dict['variable_codes']]
        #    codes = VariableCodeDescription.objects.filter(pk__in=variable_code_ids) # returns a queryset
         #   coded_value_ids = []
            # Aggregate all the coded values for each selected code
          #  for code in codes:
           #     coded_value_ids += code.variablecodedvalue_set.values_list('id', flat=True)
            # Coded values have a FK to society.  Aggregate the societies from each value
            #values = VariableCodedValue.objects.filter(id__in=coded_value_ids)
            #values = values.select_related('society','variable')
            #for value in values:
            #    result_set.add_cultural(value.society,value.variable,value)
        #except:
         #   f.write("BF_ID")

    if 'environmental_filters' in query_dict:
        criteria.append(SEARCH_ENVIRONMENTAL)
        environmental_filters = query_dict['environmental_filters']
        # There can be multiple filters, so we must aggregate the results.
        for environmental_filter in environmental_filters:
            values = EnvironmentalValue.objects.filter(variable=environmental_filter['id'])
            operator = environmental_filter['operator']
            if operator == 'inrange':
                values = values.filter(value__gt=environmental_filter['params'][0]).filter(value__lt=environmental_filter['params'][1])
            elif operator == 'outrange':
                values = values.filter(value__gt=environmental_filter['params'][1]).filter(value__lt=environmental_filter['params'][0])
            elif operator == 'gt':
                values = values.filter(value__gt=environmental_filter['params'][0])
            elif operator == 'lt':
                values = values.filter(value__lt=environmental_filter['params'][0])
            values = values.select_related('variable','environmental__society')
            # get the societies from the values
            for value in values:
                result_set.add_environmental(value.society(), value.variable, value)
    if 'geographic_regions' in query_dict:
        criteria.append(SEARCH_GEOGRAPHIC)
        geographic_region_ids = [int(x['id']) for x in query_dict['geographic_regions']]
        regions = GeographicRegion.objects.filter(pk__in=geographic_region_ids) # returns a queryset
        for region in regions:
            for society in Society.objects.filter(location__intersects=region.geom):
                result_set.add_geographic_region(society, region)
    # Filter the results to those that matched all criteria
    result_set.finalize(criteria)
    return result_set

# search/filter APIs
@api_view(['POST'])
@permission_classes((AllowAny,))
def find_societies(request):
    """
    View to find the societies that match an input request.  Currently expects
    { language_filters: [{language_ids: [1,2,3]}], variable_codes: [4,5,6...],
    environmental_filters: [{id: 1, operator: 'gt', params: [0.0]}, {id:3, operator 'inrange', params: [10.0,20.0] }] }

    Returns serialized collection of SocietyResult objects
    """
    result_set = result_set_from_query_dict(request.DATA)
    return Response(SocietyResultSetSerializer(result_set).data)

class GeographicRegionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GeographicRegionSerializer
    model = GeographicRegion
    filter_class = GeographicRegionFilter

def get_language_trees_from_query_dict(query_dict):
    if 'language_ids' in query_dict:
        language_ids = [int(x) for x in query_dict['language_ids']]
        trees = LanguageTree.objects.filter(languages__pk__in=language_ids).distinct()
    else:
        trees = None
    return trees
    
@api_view(['POST'])
@permission_classes((AllowAny,))
def trees_from_languages(request):
    from ete2 import Tree
    trees = get_language_trees_from_query_dict(request.DATA)
    if 'language_ids' in request.DATA:
        languages = request.DATA['language_ids']
        for t in trees:
            langs_in_tree = [str(l.iso_code.iso_code) for l in t.languages.all() if l.id in languages] 
            newick = Tree(t.newick_string)
            #only works if tips use isocodes
            try:
                newick.prune(langs_in_tree, preserve_branch_length=True)
            except:
                continue
            t.newick_string = newick.write(format=5)
    return Response(LanguageTreeSerializer(trees, many=True).data,)
    
@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def get_min_and_max(request):
    query_string = request.QUERY_PARAMS['query']
    query_dict = json.loads(query_string)
    if 'environmental_id' in query_dict:
        values = EnvironmentalValue.objects.filter(variable__id=query_dict['environmental_id'])
        min_value = 0
        max_value = 0
        for v in values:
            if v.value < min_value:
                min_value = v.value
            elif v.value > max_value:
                max_value = v.value
    else:
        min_value = None
        max_value = None
    return Response({'min': min_value, 'max': max_value})
    
@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((JSONRenderer,))
def bin_bfcont_data(request):
    f = open('tes.txt', 'w')
    query_string = request.QUERY_PARAMS['query']
    f.write(query_string)
    query_dict = json.loads(query_string)
    if 'bf_id' in query_dict:
        bf_variable = VariableDescription.objects.filter(id=query_dict['bf_id'])
        values = VariableCodedValue.objects.filter(variable__id=query_dict['bf_id'])
        min_value = 0.0
        max_value = 0.0
        for v in values:
            if re.search('[a-zA-Z]', v.coded_value):
                continue
            elif float(v.coded_value) < min_value:
                min_value = float(v.coded_value)
            elif float(v.coded_value) > max_value:
                max_value = float(v.coded_value)

        data_range = max_value - min_value
        bin_size = data_range / 5
        bins = []
        min_bin = min_value
        for x in range(0, 5):
            min = min_bin
            max = min_bin + bin_size
            bins.append({
                'code': x,
                'description': str(min) + ' - ' + str(max),
                'min': min_bin,
                'max': min_bin + bin_size,
                'bf_id': query_dict['bf_id']
            })
            min_bin = min_bin + bin_size + 1
        f.write(str(bins))
    else:
        min_value = None
        max_value = None

    return Response(bins)

def newick_tree(key):
    # Get a newick format tree from a language tree id
    language_tree_id =key
    try:
        language_tree = LanguageTree.objects.get(pk=language_tree_id)
    except ObjectDoesNotExist:
        raise Http404
    n = NexusReader(language_tree.file.path)
    # Remove '[&R]' from newick string
    tree = re.sub(r'\[.*?\]', '', n.trees.trees[0])
    # Remove data before the =
    try:
        tree = tree[tree.index('=')+1:]
    except ValueError:
        tree = tree
    return tree

@api_view(['GET'])
@permission_classes((AllowAny,))
def get_newick_trees(request):
    from ete2 import Tree
    trees = get_language_trees_from_query_dict(request.DATA)
    if 'language_ids' in request.DATA:
        languages = request.DATA['language_ids']
        for t in trees:
            langs_in_tree = [str(l.iso_code.iso_code) for l in t.languages.all() if l.id in languages] 
            newick = Tree(t.newick_string)
            #only works if tips use isocodes
            try:
                newick.prune(langs_in_tree, preserve_branch_length=True)
            except:
                continue
            t.newick_string = newick.write(format=5)
    return Response(LanguageTreeSerializer(trees, many=True).data,)

@api_view(['GET'])
@permission_classes((AllowAny,))
@renderer_classes((DPLACECsvRenderer,))
def csv_download(request):
    import datetime
    # Ideally these would be handled by serializers, but we've already got logic to parse a query object
    query_string = request.QUERY_PARAMS['query']
    # Need to parse the JSON
    query_dict = json.loads(query_string)
    result_set = result_set_from_query_dict(query_dict)
    response = Response(SocietyResultSetSerializer(result_set).data)
    filename = "dplace-societies-%s.csv" % datetime.datetime.now().strftime("%Y-%m-%d")
    response['Content-Disposition']  = 'attachment; filename="%s"' % filename
    return response
    