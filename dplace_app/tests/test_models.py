from dplace_app.models import *
from django.contrib.gis.geos import Polygon, Point, MultiPolygon
from django.test import TestCase


class GeographicRegionTestCase(TestCase):
    def setUp(self):
        poly = MultiPolygon(
            Polygon(((4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0), (4.0, 4.0))))
        self.geographic_region = GeographicRegion.objects.create(
            level_2_re=0,
            count=1,
            region_nam='Region1',
            continent='Continent1',
            tdwg_code=0,
            geom=poly)
        self.point_in = Point(5.0, 5.0)
        self.point_out = Point(10.0, 10.0)

    def test_point_in_region(self):
        self.assertIn(
            self.geographic_region,
            GeographicRegion.objects.filter(geom__intersects=self.point_in),
            "Point should be in geo region")

    def test_point_not_in_region(self):
        self.assertNotIn(
            self.geographic_region,
            GeographicRegion.objects.filter(geom__intersects=self.point_out),
            "Point should not be in geo region")


class EATestCase(TestCase):
    """
    Tests basic functionality of Ethnographic Atlas variable codings in model
    """

    def setUp(self):
        self.iso_code = ISOCode.objects.create(iso_code='abc')
        self.source = Source.objects.create(
            year="2014",
            author="Greenhill",
            reference="Great paper")
        self.ea_society = Society.objects.create(
            ext_id='easoc',
            name='EA Society',
            location=Point(0.0, 0.0),
            source=self.source)
        self.binford_society = Society.objects.create(
            ext_id='binfordsoc',
            name='Binford Society',
            location=Point(0.0, 0.0),
            source=self.source)
        self.variable = CulturalVariable.objects.create(
            label='EA001',
            name='Variable 1',
            source=self.source)
        self.code10 = CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='10',
            description='Code 10')
        self.code1 = CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='1',
            description='Code 1')
        self.code2 = CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='2',
            description='Code 2')
        self.value = CulturalValue.objects.create(
            variable=self.variable,
            society=self.ea_society,
            coded_value='1',
            code=self.code1,
            source=self.source)

    def test_society_coded_value(self):
        society = Society.objects.get(ext_id='easoc')
        self.assertIn(self.value, society.culturalvalue_set.all())

    def test_coded_variable(self):
        self.assertEqual(self.code1.variable, self.variable)
        self.assertEqual(self.code2.variable, self.variable)

    def test_society_variable(self):
        self.assertIn(self.ea_society, self.variable.coded_societies())
        self.assertNotIn(self.binford_society, self.variable.coded_societies())

    def test_society_code(self):
        self.assertIn(self.ea_society, self.code1.coded_societies())
        self.assertNotIn(self.ea_society, self.code2.coded_societies())

    def test_code_order(self):
        """
        Make sure 2 comes before 10
        """
        index_of_2 = index_of_10 = index = 0
        for code in self.variable.codes.all():
            if code == self.code2:
                index_of_2 = index
            elif code == self.code10:
                index_of_10 = index
            index += 1
        self.assertLess(index_of_2, index_of_10)
