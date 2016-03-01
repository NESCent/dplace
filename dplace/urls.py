from django.conf.urls import include, url
from django.contrib.sitemaps.views import sitemap
from dplace_app.sitemaps import SITEMAP

urlpatterns = [
    url(r'^', include('dplace_app.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': SITEMAP},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
]
