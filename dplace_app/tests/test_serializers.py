from django.test import TestCase
from dplace_app import models
from dplace_app.serializers import Legend, SocietyResult

# much of the testing of serializers is done in test_api, this is here to catch the
# remainder of the unexposed/untested code.


class LegendTestCase(TestCase):
    """Tests the Legend"""
    def test_name(self):
        assert Legend('name', 'svg').name == 'name'
        
    def test_svg(self):
        assert Legend('name', 'svg').svg == 'svg'


class SocietyResultTestCase(TestCase):
    """Tests for SocietyResult"""
    def setUp(self):
        self.source = models.Source.objects.create(
            year='2016',
            author='Simon Greenhill',
            reference='Greenhill (2016). Title.',
            name='EA Test Dataset'
        )
        self.language = models.Language.objects.create(
            name='language1',
            glotto_code='aaaa1234',
        )
        self.society = models.Society.objects.create(
            ext_id='society1',
            xd_id='xd1',
            name='Society1',
            source=self.source,
            language=self.language,
            focal_year='2016',
            alternate_names='Society'
        )
        self.SR = SocietyResult(self.society)
        
    def test_includes_criteria(self):
        assert self.SR.includes_criteria() == True
        assert self.SR.includes_criteria('l') == False
        assert self.SR.includes_criteria('e') == False
        assert self.SR.includes_criteria('v') == False
        assert self.SR.includes_criteria('g') == False
