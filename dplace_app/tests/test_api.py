# coding: utf8
from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from clldutils.path import Path

from dplace_app.models import *
from dplace_app.load import load
from dplace_app.loader import sources


class Test(APITestCase):
    """Tests rest-framework API"""
    def _fixture_teardown(self):
        try:
            APITestCase._fixture_teardown(self)
        except:
            pass

    def get_json(self, urlname, *args, **kw):
        kw.setdefault('format', 'json')
        reverse_args = kw.pop('reverse_args', [])
        response = self.client.get(reverse(urlname, args=reverse_args), *args, **kw)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        try:  # csv download doesn't return json
            return json.loads(response.content)
        except:
            return response.content

    def obj_in_results(self, obj, response):
        return getattr(obj, 'id', obj) in [x['id'] for x in response['results']]

    def setUp(self):
        sources._SOURCE_CACHE = {}
        load(Path(__file__).parent.joinpath('data'))

    def test_society_detail(self):
        self.client.get(reverse('view_society', args=('society1',)))

    def test_society_search(self):
        res = self.client.get(reverse('view_society', args=('society1',)))
        self.assertIn('Söciety1'.encode('utf8'), res.content)

    def test_api_variable(self):
        res = self.get_json(
            'variable-detail',
            reverse_args=[Variable.objects.get(label='1').id])
        self.assertIsInstance(res['index_categories'][0], dict)

    def test_zip_legends(self):
        response = self.client.post(reverse('download'))
        self.assertIn('attachment', response['Content-Disposition'])

    def test_get_categories(self):
        response = self.get_json('get_categories', {'query': json.dumps({})})
        self.assertIsInstance(response, list)
        response = self.get_json(
            'get_categories',
            {'query': json.dumps(dict(source=Source.objects.get(name='Ethnographic Atlas').id))})
        self.assertIsInstance(response, list)

    def test_min_and_max(self):
        response = self.get_json(
            'min_and_max',
            {'query': json.dumps(
                dict(environmental_id=Variable.objects.get(name='Rainfall').id))})
        self.assertIsInstance(response, dict)
        self.assertIn('min', response)
        self.assertIn('max', response)

    def test_cont_variable(self):
        response = self.client.get('cont_variable')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('cont_variable', {'query': 'not-json-parseable'})
        self.assertEqual(response.status_code, 404)
        response = self.client.get('cont_variable', {'query': '[]'})
        self.assertEqual(response.status_code, 404)
        response = self.get_json(
            'cont_variable',
            {'query': json.dumps(dict(bf_id=Variable.objects.get(label='2').id))})
        self.assertIsInstance(response, list)

    def test_geo_api(self):
        response = self.client.get(reverse('geographicregion-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            response.data['results'][0]['region_nam'],
            GeographicRegion.objects.get(region_nam='Region1').region_nam)

    def test_isocode_api(self):
        response_dict = self.get_json('isocode-list')
        self.assertEqual(response_dict['count'], 2)

    def test_all_languages(self):
        response_dict = self.get_json('language-list')
        self.assertEqual(response_dict['count'], 3)
        for lang in Language.objects.all():
            self.assertTrue(self.obj_in_results(lang, response_dict))

    def test_family2_languages(self):
        response_dict = self.get_json(
            'language-list',
            {'family': LanguageFamily.objects.first().id})
        self.assertEqual(response_dict['count'], 2)

    def test_all_variables(self):
        response_dict = self.get_json('variable-list')
        self.assertEqual(response_dict['count'], 5)
        self.assertEqual(
            len([x for x in response_dict['results'] if x['type'] == 'cultural']), 2)
        for name in ['Rainfall', 'Temperature', 'Subsistence economy: gathering']:
            env_var = Variable.objects.get(name=name)
            self.assertTrue(self.obj_in_results(env_var, response_dict))

    def test_category1_variables(self):
        response_dict = self.get_json(
            'variable-list',
            {'index_categories': [Category.objects.get(name='Climate').id]})
        for name, assertion in [
            ('Rainfall', self.assertTrue),
            ('Temperature', self.assertTrue),
            ('Ecology1', self.assertFalse)
        ]:
            env_var = Variable.objects.get(name=name)
            assertion(self.obj_in_results(env_var, response_dict))

    def test_code_description_order(self):
        """
        Make sure 2 comes before 10
        """
        response_dict = self.get_json(
            'codedescription-list', {'variable': Variable.objects.get(label='1').id})
        self.assertEqual(
            [res['code'] for res in response_dict['results']],
            ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'NA'])

    def test_filter_source(self):
        response_dict = self.get_json(
            'variable-list', {'source': Source.objects.get(name='Ethnographic Atlas').id})
        self.assertEqual(response_dict['count'], 2)

    def test_category2_variables(self):
        response_dict = self.get_json(
            'variable-list',
            {'index_categories': [Category.objects.get(name='Economy').id]})
        self.assertEqual(response_dict['count'], 2)

    def test_category3_variables(self):
        response_dict = self.get_json(
            'variable-list',
            {'index_categories': [Category.objects.get(name='Subsistence').id]})
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['name'],
            Variable.objects.get(label='1').name)
        self.assertFalse(self.obj_in_results(
            Variable.objects.get(label='2'), response_dict))

    def test_csv_download(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')
        response = self.get_json(
            'csv_download',
            {'query': json.dumps({'p': [
                GeographicRegion.objects.get(region_nam='Region1').id]})})
        self.assertIn('Region1'.encode('utf8'), response)

    def test_csv_download_var(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')
        response = self.get_json(
            'csv_download', 
            {'query': json.dumps({'c': ['%s-%s' % (
                CodeDescription.objects.get(code='1').variable.id,
                CodeDescription.objects.get(code='1').id)]})})
        self.assertIn('Herero', response.decode('utf8'))

    def test_trees_from_societies(self):
        response = self.get_json(
            'trees_from_societies',
            {s.ext_id: s.id for s in Society.objects.all()})
        self.assertEqual(response, [])

    #
    # find societies:
    #
    def get_results(self, urlname='find_societies', no_escape=False, **data):
        method = self.client.post
        if urlname == 'find_societies':
            method = self.client.get
            _data = []
            for k, v in data.items():
                for vv in v:
                    if no_escape:
                        _data.append((k, vv))
                    else:
                        if str(k) == 'c':
                            _data.append((k, vv))
                        else:
                            _data.append((k, json.dumps(vv)))
            data = _data
        return method(reverse(urlname), data, format='json')

    def society_in_results(self, society, response):
        return society.id in [x['society']['id'] for x in response.data['societies']]

    def test_find_societies_by_language(self):
        # Find the societies that use language1
        response = self.get_results(l=[Language.objects.get(glotto_code='aaaa1234').id])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))

    def test_find_society_by_var(self):
        response = self.get_results(c=['%s-%s' % (
            CodeDescription.objects.get(code='1').variable.id,
            CodeDescription.objects.get(code='1').id)])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_societies_by_var(self):
        serialized_codes = [
            '%s-%s' % (CodeDescription.objects.get(code=i).variable.id,
                       CodeDescription.objects.get(code=i).id) for i in ['1', '4']
        ]
        response = self.get_results(c=serialized_codes)
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_society_by_name(self):
        response = self.get_results(no_escape=True, name=['Söciety1'])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_society_by_continuous_var(self):
        response = self.get_results(c=['%s-%s-%s' % (
            Variable.objects.get(label='2').id, 0.0, 100)])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_no_societies(self):
        response = self.get_results(
            c=['%s-%s' % (CodeDescription.objects.get(code='1').variable.id,
                          CodeDescription.objects.get(code='9').id)])
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        serialized_vcs = ['%s-%s' % (
            CodeDescription.objects.get(code=i).variable.id,
            CodeDescription.objects.get(code=i).id) for i in ['1', '4']]
        serialized_lcs = [
            Language.objects.get(glotto_code=i).id for i in ['aaaa1234', 'cccc1234']]
        response = self.get_results(c=serialized_vcs, l=serialized_lcs)
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society3'), response))

    def test_empty_response(self):
        response = self.get_results()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_by_environmental_filter_gt(self):
        response = self.get_results(
            e=[[Variable.objects.get(name='Rainfall').id, 'gt', ['1.5']]])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))

    def test_find_by_environmental_filter_lt(self):
        response = self.get_results(
            e=[[Variable.objects.get(name='Rainfall').id,
                'lt', ['1.5']]])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_by_environmental_filter_inrange(self):
        response = self.get_results(
            e=[[Variable.objects.get(name='Rainfall').id,
                'inrange', ['0.0', '1.5']]])
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_by_environmental_filter_outrange(self):
        response = self.get_results(
            e=[[Variable.objects.get(name='Rainfall').id,
                'outrange', ['0.0', '3.0']]])
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))

    def test_find_by_geographic_region(self):
        """
        This uses a region that contains a single polygon around society 2
        """
        response = self.get_results(p=[GeographicRegion.objects.get(region_nam='Region2').id])
        self.assertFalse(
            self.society_in_results(Society.objects.get(ext_id='society1'), response))
        self.assertTrue(
            self.society_in_results(Society.objects.get(ext_id='society2'), response))
        self.assertIn('coordinates', response.data['societies'][0]['society']['location'])
