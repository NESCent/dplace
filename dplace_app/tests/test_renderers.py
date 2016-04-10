from django.test import TestCase

from dplace_app.renderers import DPLACECSVResults, DPLACECSVRenderer, ZipRenderer


class DPLACECSVResultsTestCase(TestCase):
    """
    Tests basic functionality of DPLACECSVResults
    """

    def setUp(self):
        self.renderer = DPLACECSVResults({})
        self.var = {'label': 'label', 'name': 'name', 'units': 'unit'}
        
    def test_field_names_for_cultural_variable(self):
        fieldnames = self.renderer.field_names_for_cultural_variable(self.var)
        for k in fieldnames:
            expected = ": %s %s" % (self.var['label'], self.var['name'])
            assert fieldnames[k].endswith(expected)
    
    def test_field_names_for_environmental_variable(self):
        name = self.renderer.field_names_for_environmental_variable(self.var)
        assert name['name'] == 'Variable: %s (%s)' % (self.var['name'], self.var['units'])


class DPLACECSVRendererTestCase(TestCase):
    """
    Tests basic functionality of DPLACECSVRenderer
    """
    def setUp(self):
        self.renderer = DPLACECSVRenderer()

    def test_media_type(self):
        assert self.renderer.media_type == 'text/csv'

    def test_format(self):
        assert self.renderer.format == 'csv'
    
    def test_safe_handling_of_no_data(self):
        assert self.renderer.render(data=None) == ''
    

class ZipRendererTestCase(TestCase):
    """
    Tests basic functionality of ZipRenderer
    """
    def setUp(self):
        self.renderer = ZipRenderer()

    def test_media_type(self):
        assert self.renderer.media_type == 'application/zip'

    def test_format(self):
        assert self.renderer.format == 'zip'
    
    def test_safe_handling_of_no_data(self):
        assert self.renderer.render(data=None) == ''
