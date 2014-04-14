from django.db.utils import IntegrityError
from django.test import TestCase
from dplace_app.models import *
from django.contrib.gis.geos import Polygon, Point
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from django.core.urlresolvers import reverse

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
        self.variable = VariableDescription.objects.create(label='EA001',name='Variable 1')
        self.code10 = VariableCodeDescription.objects.create(variable=self.variable, code='10', description='Code 10')
        self.code1 = VariableCodeDescription.objects.create(variable=self.variable, code='1', description='Code 1')
        self.code2 = VariableCodeDescription.objects.create(variable=self.variable, code='2', description='Code 2')
        self.value = VariableCodedValue.objects.create(variable=self.variable,society=self.ea_society,coded_value='1',code=self.code1)
    def test_isocode(self):
        self.assertEqual(Society.objects.get(ext_id='easoc').iso_code, self.iso_code)
    def test_society_coded_value(self):
        society = Society.objects.get(ext_id='easoc')
        self.assertIn(self.value,society.variablecodedvalue_set.all())
    def test_coded_variable(self):
        self.assertEqual(self.code1.variable,self.variable)
        self.assertEqual(self.code2.variable,self.variable)
    def test_society_variable(self):
        self.assertIn(self.ea_society, self.variable.coded_societies())
        self.assertNotIn(self.binford_society, self.variable.coded_societies())
    def test_society_code(self):
        self.assertIn(self.ea_society, self.code1.coded_societies())
        self.assertNotIn(self.ea_society, self.code2.coded_societies())
    def test_code_order(self):
        '''
        Make sure 2 comes before 10
        '''
        index_of_2 = index_of_10 = index = 0
        for code in self.variable.codes.all():
            if code == self.code2:
                index_of_2 = index
            elif code == self.code10:
                index_of_10 = index
            index += 1
        self.assertLess(index_of_2, index_of_10)

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

class FindSocietiesTestCase(APITestCase):
    '''
    Tests the find societies API
    '''
    def setUp(self):
        # make two societies
        iso_code1 = ISOCode.objects.create(iso_code='abc',location=Point(1.0,1.0))
        iso_code2 = ISOCode.objects.create(iso_code='def',location=Point(2.0,2.0))
        iso_code3 = ISOCode.objects.create(iso_code='ghi',location=Point(3.0,3.0))
        # Make languages
        language1 = Language.objects.create(name='language1',iso_code=iso_code1)
        language2 = Language.objects.create(name='language2',iso_code=iso_code2)
        language3 = Language.objects.create(name='language3',iso_code=iso_code3)

        self.society1 = Society.objects.create(ext_id='society1',name='Society1',location=Point(1.0,1.0),source='EA',iso_code=iso_code1,language=language1)
        self.society2 = Society.objects.create(ext_id='society2',name='Society2',location=Point(2.0,2.0),source='EA',iso_code=iso_code2,language=language2)
        # Society 3 has the same language characteristics as society 1 but different EA Vars
        self.society3 = Society.objects.create(ext_id='society3',name='Society3',location=Point(3.0,3.0),source='EA',iso_code=iso_code3,language=language3)

        # make a language class tree
        self.root_language_class = LanguageClass.objects.create(name='root',level=1,parent=None)
        self.parent_language_class_1 = LanguageClass.objects.create(name='parent1',level=2,parent=self.root_language_class)
        self.child_language_class_1a = LanguageClass.objects.create(name='child1',level=3,parent=self.parent_language_class_1)
        self.child_language_class_1b = LanguageClass.objects.create(name='child1',level=3,parent=self.parent_language_class_1)
        self.parent_language_class_2 = LanguageClass.objects.create(name='parent2',level=2,parent=self.root_language_class)
        self.child_language_class_2 = LanguageClass.objects.create(name='child2',level=3,parent=self.parent_language_class_2)

        # make language classifications to link a language to its class tree
        lc1 = LanguageClassification.objects.create(language=language1,
                                                    ethnologue_classification='lc1',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_1,
                                                    class_subsubfamily=self.child_language_class_1a)
        lc2 = LanguageClassification.objects.create(language=language2,
                                                    ethnologue_classification='lc2',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_2,
                                                    class_subsubfamily=self.child_language_class_2)
        lc3 = LanguageClassification.objects.create(language=language3,
                                                    ethnologue_classification='lc3',
                                                    class_family=self.root_language_class,
                                                    class_subfamily=self.parent_language_class_1,
                                                    class_subsubfamily=self.child_language_class_1b)
        # Make an EA Variable, code, and value
        variable = VariableDescription.objects.create(label='EA001',name='Variable 1')
        self.code1 = VariableCodeDescription.objects.create(variable=variable, code='1', description='Code 1')
        self.code2 = VariableCodeDescription.objects.create(variable=variable, code='2', description='Code 2')
        self.code3 = VariableCodeDescription.objects.create(variable=variable, code='3', description='Code 3')
        value1 = VariableCodedValue.objects.create(variable=variable,society=self.society1,coded_value='1',code=self.code1)
        value2 = VariableCodedValue.objects.create(variable=variable,society=self.society2,coded_value='2',code=self.code2)
        # Setup environmentals
        self.environmental1 = Environmental.objects.create(society=self.society1,
                                                           reported_location=Point(0,0),
                                                           actual_location=Point(0,0),
                                                           iso_code=iso_code1)
        self.environmental2 = Environmental.objects.create(society=self.society2,
                                                           reported_location=Point(1,1),
                                                           actual_location=Point(1,1),
                                                           iso_code=iso_code2)

        self.environmental_variable1 = EnvironmentalVariable.objects.create(name='precipitation',
                                                                            units='mm')
        self.environmental_value1 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=1.0,
                                                                      environmental=self.environmental1)
        self.environmental_value2 = EnvironmentalValue.objects.create(variable=self.environmental_variable1,
                                                                      value=2.0,
                                                                      environmental=self.environmental2)

        self.url = reverse('find_societies')
    def test_find_societies_by_root_language(self):
        language_class_ids = [self.root_language_class.pk]
        data = {'language_class_ids': language_class_ids}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertIn(self.society2.id,[x['id'] for x in response.data])
        self.assertIn(self.society3.id,[x['id'] for x in response.data])
    def test_find_societies_by_parent_language(self):
        # 1 and 3 but not 2
        language_class_ids = [self.parent_language_class_1.pk]
        data = {'language_class_ids': language_class_ids}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
        self.assertIn(self.society3.id,[x['id'] for x in response.data])
    def test_find_societies_by_parent_and_child_language(self):
        # 1 and 2 but not 3
        language_class_ids = [self.child_language_class_1a.pk, self.child_language_class_2.pk]
        data = {'language_class_ids': language_class_ids}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertIn(self.society2.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society3.id,[x['id'] for x in response.data])
    def test_find_society_by_var(self):
        data = {'variable_codes': [self.code1.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
    def test_find_societies_by_var(self):
        data = {'variable_codes': [self.code1.pk, self.code2.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertIn(self.society2.id,[x['id'] for x in response.data])
    def test_find_no_societies(self):
        data = {'variable_codes': [self.code3.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertEqual(len(response.data),0)
    def test_find_society_by_language_and_var(self):
        # 1 and 3 share a parent language class
        # 2 does not share a parent language
        # this should return only 1 and not 2 or 3
        data = {'variable_codes': [self.code1.pk, self.code2.pk],
                'language_class_ids': [self.parent_language_class_1.pk]}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society3.id,[x['id'] for x in response.data])
    def test_empty_response(self):
        response = self.client.post(self.url,{},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_find_by_environmental_filter_gt(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'gt', 'params': ['1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertNotIn(self.society1.id,[x['id'] for x in response.data])
        self.assertIn(self.society2.id,[x['id'] for x in response.data])
    def test_find_by_environmental_filter_lt(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'lt', 'params': ['1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
    def test_find_by_environmental_filter_inrange(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'inrange', 'params': ['0.0','1.5']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
    def test_find_by_environmental_filter_outrange(self):
        data = {'environmental_filters': [{'id': str(self.environmental_variable1.pk),
                                           'operator': 'outrange', 'params': ['0.0','3.0']}]}
        response = self.client.post(self.url,data,format='json')
        self.assertNotIn(self.society1.id,[x['id'] for x in response.data])
        self.assertNotIn(self.society2.id,[x['id'] for x in response.data])
