from django.conf.urls import patterns, include, url

from django.contrib.gis import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^', include('dplace_app.urls')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
)
