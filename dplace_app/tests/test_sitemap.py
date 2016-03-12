from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from dplace_app import models


class SiteMapTestCase(TestCase):
    """Tests Sitemap"""

    def setUp(self):
        self.source = models.Source.objects.create(
            year="2014",
            author="Greenhill",
            reference="Great paper")
        self.ea_society = models.Society.objects.create(
            ext_id='easoc',
            name='EA Society',
            source=self.source)
        self.binford_society = models.Society.objects.create(
            ext_id='binfordsoc',
            name='Binford Society',
            source=self.source)
        self.language1 = models.Language.objects.create(
            name='language1', glotto_code='aaaa1234'
        )
        self.language2 = models.Language.objects.create(
            name='language2', glotto_code='bbbb1234'
        )
        
        self.client = Client()
        self.url = reverse('django.contrib.sitemaps.views.sitemap')
        self.response = self.client.get(self.url)
        
    def test_society_urls(self):
        assert self.ea_society.get_absolute_url() in self.response.content
        assert self.binford_society.get_absolute_url() in self.response.content

    def test_language(self):
        assert self.language1.get_absolute_url() in self.response.content
        assert self.language2.get_absolute_url() in self.response.content
