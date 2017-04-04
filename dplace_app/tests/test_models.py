from django.test import TestCase

from dplace_app import models


class EATestCase(TestCase):
    """
    Tests basic functionality of Ethnographic Atlas variable codings in model
    """
    @classmethod
    def setUpTestData(cls):
        cls.source = models.Source.objects.create(
            year="2014",
            author="Greenhill",
            reference="Great paper")
        cls.ea_society = models.Society.objects.create(
            ext_id='easoc',
            name='EA Society',
            source=cls.source)
        cls.binford_society = models.Society.objects.create(
            ext_id='binfordsoc',
            name='Binford Society',
            source=cls.source)
        cls.variable = models.Variable.objects.create(
            label='EA001',
            name='Variable 1',
            source=cls.source)
        cls.code10 = models.CodeDescription.objects.create(
            variable=cls.variable,
            code='10',
            description='Code 10')
        cls.code1 = models.CodeDescription.objects.create(
            variable=cls.variable,
            code='1',
            description='Code 1')
        cls.code2 = models.CodeDescription.objects.create(
            variable=cls.variable,
            code='2',
            description='Code 2')
        cls.value = models.Value.objects.create(
            variable=cls.variable,
            society=cls.ea_society,
            coded_value='1',
            code=cls.code1,
            source=cls.source)

    def test_society_coded_value(self):
        society = models.Society.objects.get(ext_id='easoc')
        self.assertIn(self.value, society.value_set.all())

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
    
    def test_get_description(self):
        assert self.value.get_description() == self.value.code.description
    
    def test_get_description_no_code(self):
        obj = models.Value.objects.create(
            variable=self.variable,
            society=self.ea_society,
            coded_value='5',
            code=None,
            source=self.source
        )
        assert obj.get_description() == ''

    def test_get_absolute_url_language(self):
        L = models.Language.objects.create(
            name='test',
            glotto_code='xxxx1234'
        )
        assert L.get_absolute_url().endswith(L.glotto_code)