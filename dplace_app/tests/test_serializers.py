from django.test import TestCase
from dplace_app.serializers import Legend

# much of the testing of serializers is done in test_api, this is here to catch the
# remainder of the unexposed/untested code.


class LegendTestCase(TestCase):
    """Tests the Legend"""
    def test_name(self):
        assert Legend('name', 'svg').name == 'name'
        
    def test_svg(self):
        assert Legend('name', 'svg').svg == 'svg'
