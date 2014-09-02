__author__ = 'dan'

from dplace_app.models import *
from django.contrib.gis.geos import Polygon, Point, MultiPolygon
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from django.core.urlresolvers import reverse


class ISOCodeAPITestCase(APITestCase):
    '''
    Tests rest-framework API.  Verifies a single ISO code created can be fetched with
    HTTP 200
    '''
    def setUp(self):
        self.code = ISOCode.objects.create(iso_code='abc',location=Point(5.0,5.0))
    def test_isocode_api(self):
        url = reverse('isocode-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],1)
        self.assertEqual(response_dict['results'][0]['iso_code'],self.code.iso_code)

class VariableCodeDescriptionAPITestCase(APITestCase):
    '''
    tests rest-framework api for Variable Code Descriptions
    '''
    def setUp(self):
        self.variable = VariableDescription.objects.create(label='EA001',name='Variable 1')
        self.code1 = VariableCodeDescription.objects.create(variable=self.variable, code='1', description='Code 1')
        self.code10 = VariableCodeDescription.objects.create(variable=self.variable, code='10', description='Code 10')
        self.code2 = VariableCodeDescription.objects.create(variable=self.variable, code='2', description='Code 2')
    def test_code_description_order(self):
        '''
        Make sure 2 comes before 10
        '''
        url = reverse('variablecodedescription-list')
        data = {'variable': self.variable.id }
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
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

class GeographicRegionAPITestCase(APITestCase):
    def setUp(self):
        poly = MultiPolygon(Polygon( ((4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0), (4.0,4.0))))
        self.geographic_region = GeographicRegion.objects.create(
            level_2_re=0,
            count=1,
            region_nam='Region1',
            continent='Continent1',
            tdwg_code=0,
            geom=poly)
    def test_geo_api(self):
        url = reverse('geographicregion-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],1)
        self.assertEqual(response_dict['results'][0]['region_nam'],self.geographic_region.region_nam)

class FindSocietiesTestCase(APITestCase):
    '''
    Tests the find societies API
    Responses will be serialized SocietyResult objects
    '''
    def setUp(self):
        # make ISO codes
        iso_code1 = ISOCode.objects.create(iso_code='abc',location=Point(1.0,1.0))
        iso_code2 = ISOCode.objects.create(iso_code='def',location=Point(2.0,2.0))
        iso_code3 = ISOCode.objects.create(iso_code='ghi',location=Point(3.0,3.0))
        # Make languages
        self.languageA1 = Language.objects.create(name='languageA1',iso_code=iso_code1)
        self.languageC2 = Language.objects.create(name='languageC2',iso_code=iso_code2)
        self.languageB3 = Language.objects.create(name='languageB3',iso_code=iso_code3)
        # Make source
        self.source = Source.objects.create(year="2014", author="Greenhill", reference="Great paper")
        
        self.society1 = Society.objects.create(ext_id='society1',name='Society1',location=Point(1.0,1.0),source=self.source,iso_code=iso_code1,language=self.languageA1)
        self.society2 = Society.objects.create(ext_id='society2',name='Society2',location=Point(2.0,2.0),source=self.source,iso_code=iso_code2,language=self.languageC2)
        # Society 3 has the same language characteristics as society 1 but different EA Vars
        self.society3 = Society.objects.create(ext_id='society3',name='Society3',location=Point(3.0,3.0),source=self.source,iso_code=iso_code3,language=self.languageB3)

        # make a language class tree
        self.root_language_class = LanguageClass.objects.create(name='root',level=1,parent=None)
        self.parent_language_class_1 = LanguageClass.objects.create(name='parent1',level=2,parent=self.root_language_class)
        self.child_language_class_1a = LanguageClass.objects.create(name='child1',level=3,parent=self.parent_language_class_1)
        self.child_language_class_1b = LanguageClass.objects.create(name='child1',level=3,parent=self.parent_language_class_1)
        self.parent_language_class_2 = LanguageClass.objects.create(name='parent2',level=2,parent=self.root_language_class)
        self.child_language_class_2 = LanguageClass.objects.create(name='child2',level=3,parent=self.parent_language_class_2)

        # make language classifications to link a language to its class tree
        lc1 = LanguageClassification.objects.create(language=self.languageA1,
                                                    ethnologue_classification='lc1',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_1,
                                                    class_subsubfamily=self.child_language_class_1a)
        lc2 = LanguageClassification.objects.create(language=self.languageC2,
                                                    ethnologue_classification='lc2',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_2,
                                                    class_subsubfamily=self.child_language_class_2)
        lc3 = LanguageClassification.objects.create(language=self.languageB3,
                                                    ethnologue_classification='lc3',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_1,
                                                    class_subsubfamily=self.child_language_class_1b)
        # Make an EA Variable, code, and value
        variable = VariableDescription.objects.create(label='EA001',name='Variable 1')
        self.code1 = VariableCodeDescription.objects.create(variable=variable, code='1', description='Code 1')
        self.code2 = VariableCodeDescription.objects.create(variable=variable, code='2', description='Code 2')
        self.code3 = VariableCodeDescription.objects.create(variable=variable, code='3', description='Code 3')
        value1 = VariableCodedValue.objects.create(variable=variable,society=self.society1,coded_value='1',code=self.code1, source=self.source)
        value2 = VariableCodedValue.objects.create(variable=variable,society=self.society2,coded_value='2',code=self.code2, source=self.source)
        # Setup environmentals
        self.environmental1 = Environmental.objects.create(society=self.society1,
                                                           reported_location=Point(0,0),
                                                           actual_location=Point(0,0),
                                                           source=self.source,
                                                           iso_code=iso_code1)
        self.environmental2 = Environmental.objects.create(society=self.society2,
                                                           reported_location=Point(1,1),
                                                           actual_location=Point(1,1),
                                                           source=self.source,
                                                           iso_code=iso_code2)

        self.environmental_variable1 = EnvironmentalVariable.objects.create(name='precipitation',
                                                                            units='mm')
        self.environmental_value1 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=1.0, source=self.source,
                                                                      environmental=self.environmental1)
        self.environmental_value2 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=2.0, source=self.source,
                                                                      environmental=self.environmental2)
        # Geographic regions that contain societies
        poly2  = MultiPolygon(
            Polygon( ((1.5, 1.5), (1.5, 2.5), (2.5, 2.5), (2.5, 1.5), (1.5, 1.5)) ),
        )
        self.geographic_region2 = GeographicRegion.objects.create(
            level_2_re=2,
            count=1,
            region_nam='Region2',
            continent='Continent2',
            tdwg_code=2,
            geom=poly2
        )
        poly13 = MultiPolygon(
            Polygon( ((0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)) ),
            Polygon( ((2.5, 2.5), (2.5, 3.5), (3.5, 3.5), (3.5, 2.5), (2.5, 2.5)) ),
        )
        self.geographic_region13 = GeographicRegion.objects.create(
            level_2_re=3,
            count=2,
            region_nam='Region13',
            continent='Continent13',
            tdwg_code=3,
            geom=poly13
        )

        self.url = reverse('find_societies')
    def assertSocietyInResponse(self,society,response):
        response_society_ids = [x['society']['id'] for x in response.data['societies']]
        return self.assertIn(society.id, response_society_ids)
    def assertSocietyNotInResponse(self,society,response):
        response_society_ids = [x['society']['id'] for x in response.data['societies']]
        return self.assertNotIn(society.id, response_society_ids)
    def test_find_societies_by_language(self):
        # Find the societies that use language1
        language_ids = [self.languageA1.id]
        data = {'language_filters' : [{'language_ids': language_ids }]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
        self.assertSocietyNotInResponse(self.society3,response)
    def test_find_society_by_var(self):
        data = {'variable_codes': [self.code1.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_find_societies_by_var(self):
        data = {'variable_codes': [self.code1.pk, self.code2.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyInResponse(self.society2,response)
    def test_find_no_societies(self):
        data = {'variable_codes': [self.code3.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(len(response.data['societies']),0)
    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        language_ids = [self.languageA1.id, self.languageB3.id]
        data = {'variable_codes': [self.code1.pk, self.code2.pk],
                'language_filters' : [{'language_ids': language_ids }]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
        self.assertSocietyNotInResponse(self.society3,response)
    def test_empty_response(self):
        response = self.client.post(self.url,{},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['societies']),0)
    def test_find_by_environmental_filter_gt(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'gt', 'params': ['1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyNotInResponse(self.society1,response)
        self.assertSocietyInResponse(self.society2,response)
    def test_find_by_environmental_filter_lt(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'lt', 'params': ['1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_find_by_environmental_filter_inrange(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'inrange', 'params': ['0.0','1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_find_by_environmental_filter_outrange(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'outrange', 'params': ['0.0','3.0']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyNotInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_find_by_geographic_region(self):
        '''
        This uses a region that contains a single polygon around society 2
        '''
        data = {'geographic_regions': [str(self.geographic_region2.pk)]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society2,response)
        self.assertSocietyNotInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society3,response)
    def test_find_by_geographic_region_mpoly(self):
        '''
        This uses a region that contains two polygons that should overlap societies 1 and 3
        '''
        data = {'geographic_regions': [str(self.geographic_region13.pk)]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyInResponse(self.society3,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_language_classification_order(self):
        '''
        verify the API returns language classifications ordered by language name
        '''

        url = reverse('languageclassification-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
        index_of_A = index_of_B = index_of_C = index =0
        for result in response_dict['results']:
            if result['language']['name'] == self.languageA1.name:
                index_of_A = index
            elif result['language']['name'] == self.languageC2.name:
                index_of_C = index
            elif result['language']['name'] == self.languageB3.name:
                index_of_B = index
            index += 1
        self.assertLess(index_of_A, index_of_B)
        self.assertLess(index_of_B, index_of_C)
    def test_language_class_order(self):
        '''
        language classes should be ordered by level then name
        '''
        url = reverse('languageclass-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
        results = response_dict['results']
        def getkey(item):
            return item['level'], item['name'],
        sorted_results = sorted(results, key=getkey)
        self.assertEquals(results,sorted_results)

