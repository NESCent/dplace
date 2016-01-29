__author__ = 'dan'

import json
from dplace_app.models import *
from dplace_app.serializers import *
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
        
class GlottoCodeAPITestCase(APITestCase):
    '''Tests rest-framework API for Glottocodes'''
    def setUp(self):
        self.code = GlottoCode.objects.create(glotto_code='abcd1234')
    def test_glottocode_api(self):
        url = reverse('glottocode-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],1)
        self.assertEqual(response_dict['results'][0]['glotto_code'],self.code.glotto_code)
        
class LanguageAPITestCase(APITestCase):
    '''Tests rest-framework API for languages'''
    def setUp(self):
        self.family = LanguageFamily.objects.create(name='family1')
        self.family2 = LanguageFamily.objects.create(name='family2')
        self.glotto_codeA = GlottoCode.objects.create(glotto_code='aaaa1234')
        self.glotto_codeD = GlottoCode.objects.create(glotto_code='dddd1234')
        self.glotto_codeC = GlottoCode.objects.create(glotto_code='cccc1234')
        
        self.iso_code = ISOCode.objects.create(iso_code='abc')
        self.language1 = Language.objects.create(name='language1', family=self.family, glotto_code=self.glotto_codeA, iso_code=self.iso_code)
        self.language2 = Language.objects.create(name='language2', family=self.family2, glotto_code=self.glotto_codeD)
        self.language3 = Language.objects.create(name='language3', family=self.family2, glotto_code=self.glotto_codeC, iso_code=self.iso_code)
        
    def assertLanguageInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertIn(variable.id, response_variable_ids)
    def assertLanguageNotInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertNotIn(variable.id, response_variable_ids)
    
    def test_all_languages(self):
        url = reverse('language-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],3)
        self.assertLanguageInResponse(self.language1,response_dict)
        self.assertLanguageInResponse(self.language2,response_dict)
        self.assertLanguageInResponse(self.language3,response_dict)
        
    def test_family2_languages(self):
        url = reverse('language-list')
        data = {'family': self.family2.id};
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],2)
        self.assertLanguageNotInResponse(self.language1,response_dict)
        self.assertLanguageInResponse(self.language2,response_dict)
        self.assertLanguageInResponse(self.language3,response_dict)
        
class EnvironmentalVariableAPITestCase(APITestCase):
    '''Tests rest-framework API for Environmental Variables'''
    def setUp(self):
        self.category1 = EnvironmentalCategory.objects.create(name='Climate')
        self.category2 = EnvironmentalCategory.objects.create(name='Ecology')
        self.variable1 = EnvironmentalVariable.objects.create(name='Rainfall', category=self.category1, units='mm', codebook_info='Precipitation')
        self.variable2 = EnvironmentalVariable.objects.create(name='Temperature', category=self.category1, units='C', codebook_info='Temperature')
        self.variable3 = EnvironmentalVariable.objects.create(name='Ecology1', category=self.category2, units='', codebook_info='')
        
    def assertVariableInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertIn(variable.id, response_variable_ids)
    def assertVariableNotInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertNotIn(variable.id, response_variable_ids)
    
    def test_all_environmental_variables(self):
        url = reverse('environmentalvariable-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],3)
        self.assertVariableInResponse(self.variable1, response_dict)
        self.assertVariableInResponse(self.variable2, response_dict)
        self.assertVariableInResponse(self.variable3, response_dict)
        
    def test_category1_variables(self):
        url = reverse('environmentalvariable-list')
        data = {'category': self.category1.id}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertVariableInResponse(self.variable1, response_dict)
        self.assertVariableInResponse(self.variable2, response_dict)
        self.assertVariableNotInResponse(self.variable3, response_dict)        

class VariableCodeDescriptionAPITestCase(APITestCase):
    '''
    tests rest-framework api for Variable Code Descriptions
    '''
    def setUp(self):
        self.source_ea = Source.objects.create(year='2016', author='Simon Greenhill', reference='Greenhill (2016). Title.', name='EA Test Dataset')
        self.source_binford = Source.objects.create(year='2016', author='Russell Gray', reference='Gray (2016). Title.', name='BF Test Dataset')
        self.category1 = VariableCategory.objects.create(name='Economy')
        self.category2 = VariableCategory.objects.create(name='Demography')
        self.category3 = VariableCategory.objects.create(name='Empty Category')
        
        self.variable = VariableDescription.objects.create(label='EA001',name='Variable 1', source=self.source_ea, codebook_info='Variable 1', data_type='Categorical')
        self.variable2 = VariableDescription.objects.create(label='B002', name='Variable 2', source=self.source_binford, codebook_info='Variable 2', data_type='Continuous')
        self.variable3 = VariableDescription.objects.create(label='EA002', name='EA Variable 2', source=self.source_ea, codebook_info='EA Variable 2', data_type='Categorical')
        self.variable.save()
        self.variable2.save()
        self.variable3.save()
        self.variable.index_categories.add(self.category1, self.category2)
        self.variable2.index_categories.add(self.category2)
        self.variable3.index_categories.add(self.category1)
        self.code1 = VariableCodeDescription.objects.create(variable=self.variable, code='1', description='Code 1')
        self.code10 = VariableCodeDescription.objects.create(variable=self.variable, code='10', description='Code 10')
        self.code2 = VariableCodeDescription.objects.create(variable=self.variable, code='2', description='Code 2')
    
    def assertVariableInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertIn(variable.id, response_variable_ids)
    def assertVariableNotInResponse(self,variable,response):
        response_variable_ids = [x['id'] for x in response['results']]
        return self.assertNotIn(variable.id, response_variable_ids)
        
    def assertCategoryInResponse(self,category,response):
        response_category_ids = [x['id'] for x in response]
        return self.assertIn(category.id, response_category_ids)
    def assertCategoryNotInResponse(self,category,response):
        response_category_ids = [x['id'] for x in response]
        return self.assertNotIn(category.id, response_category_ids)
    
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
        
    def test_all_variables(self):
        url = reverse('variabledescription-list')
        response = self.client.get(url,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],3)
        self.assertVariableInResponse(self.variable, response_dict)
        self.assertVariableInResponse(self.variable2, response_dict)
        self.assertVariableInResponse(self.variable3, response_dict)
        
    def test_empty_category(self):#tests get_categories API
        url = reverse('get_categories')
        data = {'query': json.dumps({'source': self.source_ea.id})}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(len(response.data),2)
        self.assertCategoryInResponse(self.category1, response.data)
        self.assertCategoryInResponse(self.category2, response.data)
        self.assertCategoryNotInResponse(self.category3, response.data)
        
    def test_filter_source(self):
        url = reverse('variabledescription-list')
        data = {'source': self.source_ea.id};
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],2)
        self.assertVariableInResponse(self.variable, response_dict)
        self.assertVariableInResponse(self.variable3, response_dict)
        self.assertVariableNotInResponse(self.variable2, response_dict)
        
    def test_category1_variables(self):
        url = reverse('variabledescription-list')
        data = {'index_categories': [self.category1.id]}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],2)
        self.assertVariableInResponse(self.variable, response_dict)
        self.assertVariableInResponse(self.variable3, response_dict)
        self.assertVariableNotInResponse(self.variable2, response_dict)
        
    def test_category2_variables(self):
        url = reverse('variabledescription-list')
        data = {'index_categories': [self.category2.id]}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        response_dict = response.data
        self.assertEqual(response_dict['count'],2)
        self.assertVariableInResponse(self.variable, response_dict)
        self.assertVariableInResponse(self.variable2, response_dict)


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
        
class MinAndMaxTestCase(APITestCase):
    '''
    Tests the min and max API.
    This is used to get min and max values for environmental variables.
    '''
    
    def setUp(self):
    
        # make ISO codes
        iso_code1 = ISOCode.objects.create(iso_code='abc',location=Point(1.0,1.0))
        iso_code2 = ISOCode.objects.create(iso_code='def',location=Point(2.0,2.0))
        
        # make Glotto codes
        glotto_code1 = GlottoCode.objects.create(glotto_code='abcc1234')
        glotto_code2 = GlottoCode.objects.create(glotto_code='defg1234')
        
        # Make language families
        lf1 = LanguageFamily.objects.create(name='family1')
        lf2 = LanguageFamily.objects.create(name='family2')
        
        # Make languages
        self.languageA1 = Language.objects.create(name='languageA1',iso_code=iso_code1, glotto_code=glotto_code1, family=lf1)
        self.languageC2 = Language.objects.create(name='languageC2',iso_code=iso_code2, glotto_code=glotto_code2, family=lf2)
        
        # Make source
        self.source = Source.objects.create(year="2014", author="Greenhill", reference="Great paper")

        # Make societies
        self.society1 = Society.objects.create(
            ext_id='society1',
            xd_id='xd1',
            name='Society1',
            location=Point(1.0,1.0),
            source=self.source,
            language=self.languageA1,
            focal_year='2016',
            alternate_names='Society 1')
        self.society2 = Society.objects.create(
            ext_id='society2',
            xd_id='xd2',
            name='Society2',
            location=Point(2.0,2.0),
            source=self.source,
            language=self.languageC2)
    
        # Make environmental variables and values
        self.environmental1 = Environmental.objects.create(society=self.society1,reported_location=Point(0,0),
                                                           actual_location=Point(0,0),source=self.source)
        self.environmental2 = Environmental.objects.create(society=self.society2,reported_location=Point(0,0),
                                                           actual_location=Point(0,0),source=self.source)
        self.environmental3 = Environmental.objects.create(society=self.society1,reported_location=Point(0,0),
                                                           actual_location=Point(0,0),source = self.source)
        self.environmental4 = Environmental.objects.create(society=self.society2,reported_location=Point(0,0),
                                                           actual_location=Point(0,0),source=self.source)
        
        self.category1 = EnvironmentalCategory(name='Climate')
        
        self.environmental_variable1 = EnvironmentalVariable.objects.create(name='precipitation',category=self.category1,units='mm')
        self.environmental_variable2 = EnvironmentalVariable.objects.create(name='temperature',category=self.category1,units='C')
        
        self.environmental_value1 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=1.0, source=self.source,
                                                                      environmental=self.environmental1)
        self.environmental_value2 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=17.0, source=self.source,
                                                                      environmental=self.environmental2)
        self.environmental_value3 = EnvironmentalValue.objects.create(variable=self.environmental_variable2,
                                                                      value=-23.5, source=self.source,
                                                                      environmental=self.environmental3)
        self.environmental_value4 = EnvironmentalValue.objects.create(variable=self.environmental_variable2,
                                                                      value=22.65423, source=self.source,
                                                                      environmental=self.environmental4)
        
    def test_min_max(self):
        url = reverse('min_and_max')
        data = {'query': json.dumps({'environmental_id': self.environmental_variable1.id})}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['min'], '1.0000')
        self.assertEqual(response.data['max'], '17.0000')
        self.assertLess(float(response.data['min']), float(response.data['max']))
        
        data = {'query': json.dumps({'environmental_id': self.environmental_variable2.id})}
        response = self.client.get(url,data,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['min'], '-23.5000')
        self.assertEqual(response.data['max'], '22.6542')
        self.assertLess(float(response.data['min']), float(response.data['max']))
        

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
        
        # make Glotto codes
        glotto_code1 = GlottoCode.objects.create(glotto_code='abcc1234')
        glotto_code2 = GlottoCode.objects.create(glotto_code='defg1234')
        glotto_code3 = GlottoCode.objects.create(glotto_code='ghij1234')
        
        # Make language families
        lf1 = LanguageFamily.objects.create(name='family1')
        lf2 = LanguageFamily.objects.create(name='family2')
        lf3 = LanguageFamily.objects.create(name='family3')
        
        # Make languages
        self.languageA1 = Language.objects.create(name='languageA1',iso_code=iso_code1, glotto_code=glotto_code1, family=lf1)
        self.languageC2 = Language.objects.create(name='languageC2',iso_code=iso_code2, glotto_code=glotto_code2, family=lf2)
        self.languageB3 = Language.objects.create(name='languageB3',iso_code=iso_code3, glotto_code=glotto_code3, family=lf3)
        
        # Make source
        self.source = Source.objects.create(year="2014", author="Greenhill", reference="Great paper")
        
        self.society1 = Society.objects.create(
            ext_id='society1',
            xd_id='xd1',
            name='Society1',
            location=Point(1.0,1.0),
            source=self.source,
            language=self.languageA1,
            focal_year='2016',
            alternate_names='Society 1')
        self.society2 = Society.objects.create(
            ext_id='society2',
            xd_id='xd2',
            name='Society2',
            location=Point(2.0,2.0),
            source=self.source,
            language=self.languageC2)
        # Society 3 has the same language characteristics as society 1 but different EA Vars
        self.society3 = Society.objects.create(
            ext_id='society3',
            xd_id='xd1',
            name='Society3',
            location=Point(3.0,3.0),
            source=self.source,
            language=self.languageB3)
        
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
        classifications = LanguageSerializer([l for l in Language.objects.all().filter(name=self.languageA1.name)],many=True)
        data = {'language_classifications' : classifications.data }
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
        self.assertSocietyNotInResponse(self.society3,response)
    def test_find_society_by_var(self):
        data = {'variable_codes': VariableCodeDescriptionSerializer([self.code1],many=True).data}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society2,response)
    def test_find_societies_by_var(self):
        serialized_codes = VariableCodeDescriptionSerializer([self.code1,self.code2],many=True).data
        data = {'variable_codes': serialized_codes}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyInResponse(self.society2,response)
    def test_find_no_societies(self):
        data = {'variable_codes': VariableCodeDescriptionSerializer([self.code3],many=True).data }
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(len(response.data['societies']),0)
    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        serialized_vcs = VariableCodeDescriptionSerializer([self.code1, self.code2], many=True).data
        language_classifications = Language.objects.filter(id__in=[self.languageA1.id, self.languageB3.id])
        serialized_lcs = LanguageSerializer(language_classifications, many=True).data
        data = {'variable_codes': serialized_vcs,
                'language_classifications' : serialized_lcs}
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
        data = {'geographic_regions': [GeographicRegionSerializer(self.geographic_region2).data]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society2,response)
        self.assertSocietyNotInResponse(self.society1,response)
        self.assertSocietyNotInResponse(self.society3,response)
    def test_find_by_geographic_region_mpoly(self):
        '''
        This uses a region that contains two polygons that should overlap societies 1 and 3
        '''
        data = {'geographic_regions': [GeographicRegionSerializer(self.geographic_region13).data]}
        response = self.client.post(self.url,data,format='json')
        self.assertSocietyInResponse(self.society1,response)
        self.assertSocietyInResponse(self.society3,response)
        self.assertSocietyNotInResponse(self.society2,response)

