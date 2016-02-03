from django.test import TestCase

from dplace_app import models


class EATestCase(TestCase):
    """
    Tests basic functionality of Ethnographic Atlas variable codings in model
    """

    def setUp(self):
        self.iso_code = models.ISOCode.objects.create(iso_code='abc')
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
        self.variable = models.CulturalVariable.objects.create(
            label='EA001',
            name='Variable 1',
            source=self.source)
        self.code10 = models.CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='10',
            description='Code 10')
        self.code1 = models.CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='1',
            description='Code 1')
        self.code2 = models.CulturalCodeDescription.objects.create(
            variable=self.variable,
            code='2',
            description='Code 2')
        self.value = models.CulturalValue.objects.create(
            variable=self.variable,
            society=self.ea_society,
            coded_value='1',
            code=self.code1,
            source=self.source)

    def test_society_coded_value(self):
        society = models.Society.objects.get(ext_id='easoc')
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
