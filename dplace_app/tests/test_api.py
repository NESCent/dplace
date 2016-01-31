from __future__ import unicode_literals
import json

from django.contrib.gis.geos import Polygon, Point, MultiPolygon
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dplace_app.serializers import (
    GeographicRegionSerializer, LanguageSerializer, VariableCodeDescriptionSerializer,
)
from dplace_app import models


class Test(APITestCase):
    def get_json(self, urlname, *args, **kw):
        kw.setdefault('format', 'json')
        response = self.client.get(reverse(urlname), *args, **kw)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

    def obj_in_results(self, obj, response):
        return getattr(obj, 'id', obj) in [x['id'] for x in response['results']]


class ISOCodeAPITestCase(Test):
    """
    Tests rest-framework API.  Verifies a single ISO code created can be fetched with
    HTTP 200
    """

    def setUp(self):
        self.code = models.ISOCode.objects.create(iso_code='abc', location=Point(5.0, 5.0))

    def test_isocode_api(self):
        response_dict = self.get_json('isocode-list')
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(response_dict['results'][0]['iso_code'], self.code.iso_code)


class GlottoCodeAPITestCase(Test):
    """Tests rest-framework API for Glottocodes"""

    def setUp(self):
        self.code = models.GlottoCode.objects.create(glotto_code='abcd1234')

    def test_glottocode_api(self):
        response_dict = self.get_json('glottocode-list')
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['glotto_code'], self.code.glotto_code)


class LanguageAPITestCase(Test):
    """Tests rest-framework API for languages"""

    def setUp(self):
        self.family = models.LanguageFamily.objects.create(name='family1')
        self.family2 = models.LanguageFamily.objects.create(name='family2')
        self.glotto_codeA = models.GlottoCode.objects.create(glotto_code='aaaa1234')
        self.glotto_codeD = models.GlottoCode.objects.create(glotto_code='dddd1234')
        self.glotto_codeC = models.GlottoCode.objects.create(glotto_code='cccc1234')

        self.iso_code = models.ISOCode.objects.create(iso_code='abc')
        self.language1 = models.Language.objects.create(
            name='language1',
            family=self.family,
            glotto_code=self.glotto_codeA,
            iso_code=self.iso_code)
        self.language2 = models.Language.objects.create(
            name='language2',
            family=self.family2,
            glotto_code=self.glotto_codeD)
        self.language3 = models.Language.objects.create(
            name='language3',
            family=self.family2,
            glotto_code=self.glotto_codeC,
            iso_code=self.iso_code)

    def test_all_languages(self):
        response_dict = self.get_json('language-list')
        self.assertEqual(response_dict['count'], 3)
        self.assertTrue(self.obj_in_results(self.language1, response_dict))
        self.assertTrue(self.obj_in_results(self.language2, response_dict))
        self.assertTrue(self.obj_in_results(self.language3, response_dict))

    def test_family2_languages(self):
        response_dict = self.get_json('language-list', {'family': self.family2.id})
        self.assertEqual(response_dict['count'], 2)
        self.assertFalse(self.obj_in_results(self.language1, response_dict))
        self.assertTrue(self.obj_in_results(self.language2, response_dict))
        self.assertTrue(self.obj_in_results(self.language3, response_dict))


class EnvironmentalVariableAPITestCase(Test):
    """Tests rest-framework API for Environmental Variables"""

    def setUp(self):
        self.category1 = models.EnvironmentalCategory.objects.create(name='Climate')
        self.category2 = models.EnvironmentalCategory.objects.create(name='Ecology')
        self.variable1 = models.EnvironmentalVariable.objects.create(
            name='Rainfall',
            category=self.category1,
            units='mm',
            codebook_info='Precipitation')
        self.variable2 = models.EnvironmentalVariable.objects.create(
            name='Temperature',
            category=self.category1,
            units='C',
            codebook_info='Temperature')
        self.variable3 = models.EnvironmentalVariable.objects.create(
            name='Ecology1',
            category=self.category2,
            units='',
            codebook_info='')

    def test_all_environmental_variables(self):
        response_dict = self.get_json('environmentalvariable-list')
        self.assertEqual(response_dict['count'], 3)
        self.assertTrue(self.obj_in_results(self.variable1, response_dict))
        self.assertTrue(self.obj_in_results(self.variable2, response_dict))
        self.assertTrue(self.obj_in_results(self.variable3, response_dict))

    def test_category1_variables(self):
        response_dict = self.get_json('environmentalvariable-list',
                                      {'category': self.category1.id})
        self.assertTrue(self.obj_in_results(self.variable1, response_dict))
        self.assertTrue(self.obj_in_results(self.variable2, response_dict))
        self.assertFalse(self.obj_in_results(self.variable3, response_dict))


class VariableCodeDescriptionAPITestCase(Test):
    """
    tests rest-framework api for Variable Code Descriptions
    """

    def setUp(self):
        self.source_ea = models.Source.objects.create(
            year='2016',
            author='Simon Greenhill',
            reference='Greenhill (2016). Title.',
            name='EA Test Dataset')
        self.source_binford = models.Source.objects.create(
            year='2016',
            author='Russell Gray',
            reference='Gray (2016). Title.',
            name='BF Test Dataset')
        self.category1 = models.VariableCategory.objects.create(name='Economy')
        self.category2 = models.VariableCategory.objects.create(name='Demography')

        self.variable = models.VariableDescription.objects.create(
            label='EA001',
            name='Variable 1',
            source=self.source_ea,
            codebook_info='Variable 1',
            data_type='Categorical')
        self.variable2 = models.VariableDescription.objects.create(
            label='B002',
            name='Variable 2',
            source=self.source_binford,
            codebook_info='Variable 2',
            data_type='Continuous')
        self.variable.save()
        self.variable2.save()
        self.variable.index_categories.add(self.category1, self.category2)
        self.variable2.index_categories.add(self.category2)
        self.code1 = models.VariableCodeDescription.objects.create(
            variable=self.variable,
            code='1',
            description='Code 1')
        self.code10 = models.VariableCodeDescription.objects.create(
            variable=self.variable,
            code='10',
            description='Code 10')
        self.code2 = models.VariableCodeDescription.objects.create(
            variable=self.variable,
            code='2',
            description='Code 2')

    def test_code_description_order(self):
        """
        Make sure 2 comes before 10
        """
        response_dict = self.get_json('variablecodedescription-list',
                                      {'variable': self.variable.id})
        index_of_1 = index_of_2 = index_of_10 = index = 0
        for result in response_dict['results']:
            if result['code'] == self.code1.code:
                index_of_1 = index
            elif result['code'] == self.code2.code:
                index_of_2 = index
            elif result['code'] == self.code10.code:
                index_of_10 = index
            index += 1
        self.assertLess(index_of_1, index_of_2)
        self.assertLess(index_of_2, index_of_10)

    def test_all_variables(self):
        response_dict = self.get_json('variabledescription-list')
        self.assertEqual(response_dict['count'], 2)
        self.assertTrue(self.obj_in_results(self.variable, response_dict))
        self.assertTrue(self.obj_in_results(self.variable2, response_dict))

    def test_filter_source(self):
        response_dict = self.get_json('variabledescription-list',
                                      {'source': self.source_ea.id})
        self.assertEqual(response_dict['count'], 1)
        self.assertTrue(self.obj_in_results(self.variable, response_dict))
        self.assertFalse(self.obj_in_results(self.variable2, response_dict))

    def test_category1_variables(self):
        response_dict = self.get_json('variabledescription-list',
                                      {'index_categories': [self.category1.id]})
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(response_dict['results'][0]['name'], self.variable.name)
        self.assertFalse(self.obj_in_results(self.variable2, response_dict))

    def test_category2_variables(self):
        response_dict = self.get_json('variabledescription-list',
                                      {'index_categories': [self.category2.id]})
        self.assertEqual(response_dict['count'], 2)
        self.assertTrue(self.obj_in_results(self.variable, response_dict))
        self.assertTrue(self.obj_in_results(self.variable2, response_dict))


class GeographicRegionAPITestCase(APITestCase):
    def setUp(self):
        poly = MultiPolygon(
            Polygon(((4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0), (4.0, 4.0))))
        self.geographic_region = models.GeographicRegion.objects.create(
            level_2_re=0,
            count=1,
            region_nam='Region1',
            continent='Continent1',
            tdwg_code=0,
            geom=poly)

    def test_geo_api(self):
        response = self.client.get(reverse('geographicregion-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(
            response.data['results'][0]['region_nam'], self.geographic_region.region_nam)


class FindSocietiesTestCase(Test):
    """
    Tests the find societies API
    Responses will be serialized SocietyResult objects
    """

    def setUp(self):
        # make ISO codes
        iso_code1 = models.ISOCode.objects.create(iso_code='abc', location=Point(1.0, 1.0))
        iso_code2 = models.ISOCode.objects.create(iso_code='def', location=Point(2.0, 2.0))
        iso_code3 = models.ISOCode.objects.create(iso_code='ghi', location=Point(3.0, 3.0))

        # make Glotto codes
        glotto_code1 = models.GlottoCode.objects.create(glotto_code='abcc1234')
        glotto_code2 = models.GlottoCode.objects.create(glotto_code='defg1234')
        glotto_code3 = models.GlottoCode.objects.create(glotto_code='ghij1234')

        # Make language families
        lf1 = models.LanguageFamily.objects.create(name='family1')
        lf2 = models.LanguageFamily.objects.create(name='family2')
        lf3 = models.LanguageFamily.objects.create(name='family3')

        # Make languages
        self.languageA1 = models.Language.objects.create(
            name='languageA1',
            iso_code=iso_code1,
            glotto_code=glotto_code1,
            family=lf1)
        self.languageC2 = models.Language.objects.create(
            name='languageC2',
            iso_code=iso_code2,
            glotto_code=glotto_code2,
            family=lf2)
        self.languageB3 = models.Language.objects.create(
            name='languageB3',
            iso_code=iso_code3,
            glotto_code=glotto_code3,
            family=lf3)

        # Make source
        self.source = models.Source.objects.create(
            year="2014",
            author="Greenhill",
            reference="Great paper")

        self.society1 = models.Society.objects.create(
            ext_id='society1',
            xd_id='xd1',
            name='Society1',
            location=Point(1.0, 1.0),
            source=self.source,
            language=self.languageA1,
            focal_year='2016',
            alternate_names='Society 1')
        self.society2 = models.Society.objects.create(
            ext_id='society2',
            xd_id='xd2',
            name='Society2',
            location=Point(2.0, 2.0),
            source=self.source,
            language=self.languageC2)
        # Society 3 has the same language characteristics as society 1
        # but different EA Vars
        self.society3 = models.Society.objects.create(
            ext_id='society3',
            xd_id='xd1',
            name='Society3',
            location=Point(3.0, 3.0),
            source=self.source,
            language=self.languageB3)

        # Make an EA Variable, code, and value
        variable = models.VariableDescription.objects.create(label='EA001', name='Variable 1')
        self.code1 = models.VariableCodeDescription.objects.create(
            variable=variable,
            code='1',
            description='Code 1')
        self.code2 = models.VariableCodeDescription.objects.create(
            variable=variable,
            code='2',
            description='Code 2')
        self.code3 = models.VariableCodeDescription.objects.create(
            variable=variable,
            code='3',
            description='Code 3')
        models.VariableCodedValue.objects.create(
            variable=variable,
            society=self.society1,
            coded_value='1',
            code=self.code1,
            source=self.source)
        models.VariableCodedValue.objects.create(
            variable=variable,
            society=self.society2,
            coded_value='2',
            code=self.code2,
            source=self.source)

        # Setup environmentals
        self.environmental1 = models.Environmental.objects.create(
            society=self.society1,
            reported_location=Point(0, 0),
            actual_location=Point(0, 0),
            source=self.source,
            iso_code=iso_code1)
        self.environmental2 = models.Environmental.objects.create(
            society=self.society2,
            reported_location=Point(1, 1),
            actual_location=Point(1, 1),
            source=self.source,
            iso_code=iso_code2)

        self.environmental_variable1 = models.EnvironmentalVariable.objects.create(
            name='precipitation',
            units='mm')
        self.environmental_value1 = models.EnvironmentalValue.objects.create(
            variable=self.environmental_variable1,
            value=1.0, source=self.source,
            environmental=self.environmental1)
        self.environmental_value2 = models.EnvironmentalValue.objects.create(
            variable=self.environmental_variable1,
            value=2.0, source=self.source,
            environmental=self.environmental2)
        # Geographic regions that contain societies
        poly2 = MultiPolygon(
            Polygon(((1.5, 1.5), (1.5, 2.5), (2.5, 2.5), (2.5, 1.5), (1.5, 1.5))),
        )
        self.geographic_region2 = models.GeographicRegion.objects.create(
            level_2_re=2,
            count=1,
            region_nam='Region2',
            continent='Continent2',
            tdwg_code=2,
            geom=poly2
        )
        poly13 = MultiPolygon(
            Polygon(((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5))),
            Polygon(((2.5, 2.5), (2.5, 3.5), (3.5, 3.5), (3.5, 2.5), (2.5, 2.5))),
        )
        self.geographic_region13 = models.GeographicRegion.objects.create(
            level_2_re=3,
            count=2,
            region_nam='Region13',
            continent='Continent13',
            tdwg_code=3,
            geom=poly13
        )

    def get_results(self, urlname='find_societies', **data):
        return self.client.post(reverse(urlname), data or {}, format='json')

    def society_in_results(self, society, response):
        return society.id in [x['society']['id'] for x in response.data['societies']]

    def test_find_societies_by_language(self):
        # Find the societies that use language1
        classifications = LanguageSerializer(
            [l for l in models.Language.objects.all().filter(name=self.languageA1.name)],
            many=True)
        response = self.get_results(language_classifications=classifications.data)
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))
        self.assertFalse(self.society_in_results(self.society3, response))

    def test_find_society_by_var(self):
        response = self.get_results(variable_codes=VariableCodeDescriptionSerializer(
            [self.code1], many=True).data)
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))

    def test_find_societies_by_var(self):
        serialized_codes = VariableCodeDescriptionSerializer([self.code1, self.code2],
                                                             many=True).data
        response = self.get_results(variable_codes=serialized_codes)
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertTrue(self.society_in_results(self.society2, response))

    def test_find_no_societies(self):
        response = self.get_results(
            variable_codes=VariableCodeDescriptionSerializer([self.code3],
                                                             many=True).data)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        serialized_vcs = VariableCodeDescriptionSerializer(
            [self.code1, self.code2], many=True).data
        language_classifications = models.Language.objects.filter(
            id__in=[self.languageA1.id, self.languageB3.id])
        serialized_lcs = LanguageSerializer(language_classifications, many=True).data
        response = self.get_results(
            variable_codes=serialized_vcs, language_classifications=serialized_lcs)
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))
        self.assertFalse(self.society_in_results(self.society3, response))

    def test_empty_response(self):
        response = self.get_results()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_by_environmental_filter_gt(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.environmental_variable1.pk),
                 'operator': 'gt',
                 'params': ['1.5']}])
        self.assertTrue(self.society_in_results(self.society2, response))
        self.assertFalse(self.society_in_results(self.society1, response))

    def test_find_by_environmental_filter_lt(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.environmental_variable1.pk),
                 'operator': 'lt',
                 'params': ['1.5']}])
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))

    def test_find_by_environmental_filter_inrange(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.environmental_variable1.pk),
                 'operator': 'inrange',
                 'params': ['0.0', '1.5']}])
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))

    def test_find_by_environmental_filter_outrange(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'outrange',
                                           'params': ['0.0', '3.0']}]}
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.environmental_variable1.pk),
                 'operator': 'outrange',
                 'params': ['0.0', '3.0']}])
        self.assertFalse(self.society_in_results(self.society1, response))
        self.assertFalse(self.society_in_results(self.society2, response))

    def test_find_by_geographic_region(self):
        """
        This uses a region that contains a single polygon around society 2
        """
        response = self.get_results(
            geographic_regions=[GeographicRegionSerializer(self.geographic_region2).data])
        self.assertFalse(self.society_in_results(self.society1, response))
        self.assertTrue(self.society_in_results(self.society2, response))
        self.assertFalse(self.society_in_results(self.society3, response))

    def test_find_by_geographic_region_mpoly(self):
        """
        This uses a region that contains two polygons that should overlap
        societies 1 and 3
        """
        response = self.get_results(
            geographic_regions=[
                GeographicRegionSerializer(self.geographic_region13).data])
        self.assertTrue(self.society_in_results(self.society1, response))
        self.assertTrue(self.society_in_results(self.society3, response))
        self.assertFalse(self.society_in_results(self.society2, response))

    def test_csv_download(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')

        response = self.get_results(
            urlname='csv_download',
            geographic_regions=[GeographicRegionSerializer(self.geographic_region13).data]
        )
        self.assertIn('Region13', response.content)
