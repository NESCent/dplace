from django.db.utils import IntegrityError
from django.test import TestCase
from dplace_app.models import *
from django.contrib.gis.geos import Polygon, Point

class ISOCodeTestCase(TestCase):
    '''
    Tests basic Geographic functionality of ISOCode models
    '''
    def setUp(self):
        ISOCode.objects.create(iso_code='abc',location=Point(5.0,5.0))
        ISOCode.objects.create(iso_code='def',location=Point(10.0,10.0))
    def test_isocodes(self):
        poly = Polygon( ((4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0), (4.0,4.0)))
        self.assertIn(ISOCode.objects.get(iso_code='abc'), ISOCode.objects.filter(location__intersects=poly), "ISO Code should be in region")
        self.assertNotIn(ISOCode.objects.get(iso_code='def'), ISOCode.objects.filter(location__intersects=poly), "ISO Code should not be in region")

class EATestCase(TestCase):
    '''
    Tests basic functionality of Ethnographic Atlas variable codings in model
    '''
    def setUp(self):
        self.iso_code = ISOCode.objects.create(iso_code='abc',location=Point(5.0,5.0))
        self.ea_society = Society.objects.create(ext_id='easoc',name='EA Society',location=Point(0.0,0.0),source='EA',iso_code=self.iso_code)
        self.binford_society = Society.objects.create(ext_id='binfordsoc',name='Binford Society',location=Point(0.0,0.0),source='Binford',iso_code=self.iso_code)
        self.variable = EAVariableDescription.objects.create(number=1,name='Variable 1')
        self.code1 = EAVariableCodeDescription.objects.create(variable=self.variable, code='1', description='Code 1')
        self.code2 = EAVariableCodeDescription.objects.create(variable=self.variable, code='2', description='Code 2')
        self.value = EAVariableCodedValue.objects.create(variable=self.variable,society=self.ea_society,coded_value='1',code=self.code1)
    def test_isocode(self):
        self.assertEqual(Society.objects.get(ext_id='easoc').iso_code, self.iso_code)
    def test_society_coded_value(self):
        society = Society.objects.get(ext_id='easoc')
        self.assertIn(self.value,society.eavariablecodedvalue_set.all())
    def test_coded_variable(self):
        self.assertEqual(self.code1.variable,self.variable)
        self.assertEqual(self.code2.variable,self.variable)
