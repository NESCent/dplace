from django.conf.urls import url, include
from django.views.generic.base import RedirectView

from rest_framework import routers
from rest_framework import renderers
from dplace_app import views, api_views

router = routers.DefaultRouter()
router.register(r'variables', api_views.CulturalVariableViewSet)
router.register(r'categories', api_views.CulturalCategoryViewSet)
router.register(r'codes', api_views.CulturalCodeDescriptionViewSet)
router.register(r'values', api_views.CulturalValueViewSet)
router.register(r'societies', api_views.SocietyViewSet)
router.register(r'environmental_categories', api_views.EnvironmentalCategoryViewSet)
router.register(r'environmental_variables', api_views.EnvironmentalVariableViewSet)
router.register(r'environmentals', api_views.EnvironmentalViewSet)
router.register(r'environmental_values', api_views.EnvironmentalValueViewSet)
router.register(r'isocodes', api_views.ISOCodeViewSet)
router.register(r'language_families', api_views.LanguageFamilyViewSet)
router.register(r'languages', api_views.LanguageViewSet)
router.register(r'language_trees', api_views.LanguageTreeViewSet)
router.register(r'geographic_regions', api_views.GeographicRegionViewSet)
router.register(r'sources', api_views.SourceViewSet)
router.register(r'language_tree_labels', api_views.LanguageTreeLabelsViewSet)

urlpatterns = [

    url(r'^$', RedirectView.as_view(url='angular/', permanent=True), name='home'),
    url(r'^society/(?P<society_id>.*)$',
        api_views.SocietyViewSet.as_view(
            {'get': 'detail'},
            renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name='view_society'),
    url(r'^societies/search=(?P<name>.*)$',
        api_views.SocietyViewSet.as_view(
            {'get': 'search'},
            renderer_classes=[renderers.TemplateHTMLRenderer]
        ),
        name='search_society'),
    url(r'^language/(?P<glottocode>.*)$',
        views.view_language,
        name='view_language'),
    url(r'^angular/$', views.angular, name='angular'),
    # API
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/find_societies', api_views.find_societies, name='find_societies'),
    url(r'^api/v1/min_and_max', api_views.get_min_and_max, name="min_and_max"),
    url(r'^api/v1/cont_variable', api_views.bin_cont_data, name="cont_variable"),
    url(r'^api/v1/get_categories', api_views.get_categories, name="get_categories"),
    url(r'^api/v1/get_dataset_sources',
        api_views.get_dataset_sources,
        name="get_dataset_sources"),
    url(r'^api/v1/csv_download', api_views.csv_download, name='csv_download'),
    url(r'^api/v1/zip', api_views.zip_legends, name='zip_legends'),

    # catch anything else and let decide angular what to do
    url(r'^.+?/$', views.angular),

]
