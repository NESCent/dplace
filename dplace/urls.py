from django.conf.urls import include, url

from django.contrib.gis import admin
admin.autodiscover()

urlpatterns = [
    url(r'^', include('dplace_app.urls')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
]
