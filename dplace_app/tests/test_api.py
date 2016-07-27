# coding: utf8
from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dplace_app.models import *
from dplace_app.load.geographic import load_regions
from dplace_app.load.environmental import load_environmental_var, load_environmental
from dplace_app.load.variables import load_vars, load_codes
from dplace_app.load.values import load_data
from dplace_app.load import sources
from dplace_app.tests.util import data_path
from dplace_app.load.util import csv_dict_reader


class Test(APITestCase):
    """Tests rest-framework API"""
    _data = {}

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

    def set(self, model, suffix, **kw):
        obj = model.objects.create(**kw)
        obj.save()
        self._data['%s%s' % (model.__name__, suffix)] = obj
        return obj

    def get(self, model, suffix):
        return self._data['%s%s' % (model.__name__, suffix)]

    def setUp(self):
        sources._SOURCE_CACHE = {}
        load_regions(data_path('regions.geojson'))
        load_environmental_var(csv_dict_reader(data_path('envvariables.csv')))
        load_vars(csv_dict_reader(data_path('variables.csv')))
        source_ea = Source.objects.get(name='Ethnographic Atlas')
        load_codes(csv_dict_reader(data_path('codes.csv')))

        family1 = self.set(LanguageFamily, 1, name='family1')
        family2 = self.set(LanguageFamily, 2, name='family2')
        iso_code = self.set(ISOCode, 1, iso_code='abc')
        language1 = self.set(
            Language, 1,
            name='language1', family=family1, glotto_code='aaaa1234', iso_code=iso_code)
        language2 = self.set(
            Language, 2,
            name='language2', family=family2, glotto_code='dddd1234')
        language3 = self.set(
            Language, 3,
            name='language3', family=family2, glotto_code='cccc1234', iso_code=iso_code)    
        tree1 = self.set(
            LanguageTree, 1,
            newick_string='((aaaa1234:1,abc:1,abun1254:1)abun1252:1);',
            name='tree',
            source=source_ea)
        tree2 = self.set(
            LanguageTree, 2,
            newick_string='((aaaa1234:1,abc:1,abun1254:1)abun1252:1);',
            name='tree.glotto.trees',
            source=source_ea)

        label1 = self.set(
            LanguageTreeLabels, 1,
            languageTree=tree1, label='aaaa1234',
            language=language1
        )
        label2 = self.set(
            LanguageTreeLabels, 2, 
            languageTree=tree1, label='abun1254',
            language=language2
        )
        label3 = self.set(
            LanguageTreeLabels, 3,
            languageTree=tree2, label='abun1252',
            language=language3
        )
        tree1.taxa.add(label1)
        tree1.taxa.add(label2)
        tree2.taxa.add(label3)

        society1 = self.set(
            Society, 1,
            ext_id='society1',
            xd_id='xd1',
            name='Söciety1',
            region=GeographicRegion.objects.get(region_nam='Region1'),
            source=source_ea,
            language=language1,
            focal_year='2016',
            alternate_names='Society 1')
        society2 = self.set(
            Society, 2,
            ext_id='society2',
            xd_id='xd2',
            region=GeographicRegion.objects.get(region_nam='Region2'),
            name='Society2',
            source=source_ea,
            language=language2)
        # Society 3 has the same language characteristics as society 1
        # but different EA Vars
        self.set(
            Society, 3,
            ext_id='society3',
            xd_id='xd1',
            region=GeographicRegion.objects.get(region_nam='Region1'),
            name='Society3',
            source=source_ea,
            language=language3)

        sequenceLabel1 = self.set(
            LanguageTreeLabelsSequence, 1,
            society = society1, labels = label1,
            fixed_order=0
        )
        sequenceLabel2 = self.set(
            LanguageTreeLabelsSequence, 2,
            society = society1, labels = label2,
            fixed_order=0
        )
        sequenceLabel3 = self.set(
            LanguageTreeLabelsSequence, 3,
            society = society2, labels = label3,
            fixed_order=0
        )
        sequenceLabel4 = self.set(
            LanguageTreeLabelsSequence, 4,
            society = society2, labels = label3,
            fixed_order=1
        )

        load_data(csv_dict_reader(data_path('data.csv')))
        load_environmental(csv_dict_reader(data_path('envdata.csv')))

    def test_society_detail(self):
        self.client.get(reverse('view_society', args=('society1',)))

    def test_society_search(self):
        res = self.client.get(reverse('view_society', args=('society1',)))
        self.assertIn('Söciety1'.encode('utf8'), res.content)

    def test_api_culturalcategory(self):
        res = self.get_json(
            'culturalcategory-detail',
            reverse_args=[CulturalCategory.objects.get(name='Economy').id])
        self.assertIsInstance(res['index_variables'][0], dict)

    def test_api_culturalvariable(self):
        res = self.get_json(
            'culturalvariable-detail',
            reverse_args=[CulturalVariable.objects.get(label='EA001').id])
        self.assertIsInstance(res['index_categories'][0], dict)

    def test_zip_legends(self):
        response = self.client.post(reverse('zip_legends'))
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
                dict(environmental_id=EnvironmentalVariable.objects.get(name='Rainfall').id))})
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
            {'query': json.dumps(dict(bf_id=CulturalVariable.objects.get(label='B002').id))})
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
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['iso_code'], self.get(ISOCode, 1).iso_code)

    def test_all_languages(self):
        response_dict = self.get_json('language-list')
        self.assertEqual(response_dict['count'], 3)
        for i in [1, 2, 3]:
            self.assertTrue(
                self.obj_in_results(self.get(Language, i), response_dict))

    def test_family2_languages(self):
        response_dict = self.get_json(
            'language-list',
            {'family': self.get(LanguageFamily, 2).id})
        self.assertEqual(response_dict['count'], 2)
        self.assertFalse(self.obj_in_results(self.get(Language, 1), response_dict))

    def test_all_environmental_variables(self):
        response_dict = self.get_json('environmentalvariable-list')
        self.assertEqual(response_dict['count'], 3)
        for name in ['Rainfall', 'Temperature', 'Ecology1']:
            env_var = EnvironmentalVariable.objects.get(name=name)
            self.assertTrue(self.obj_in_results(env_var, response_dict))

    def test_env_category1_variables(self):
        response_dict = self.get_json(
            'environmentalvariable-list',
            {'category': EnvironmentalCategory.objects.get(name='Climate').id})
        for name, assertion in [
            ('Rainfall', self.assertTrue),
            ('Temperature', self.assertTrue),
            ('Ecology1', self.assertFalse)
        ]:
            env_var = EnvironmentalVariable.objects.get(name=name)
            assertion(self.obj_in_results(env_var, response_dict))

    def test_code_description_order(self):
        """
        Make sure 2 comes before 10
        """
        response_dict = self.get_json(
            'culturalcodedescription-list',
            {'variable': CulturalVariable.objects.get(label='EA001').id})
        self.assertEqual(
            [res['code'] for res in response_dict['results']],
            [CulturalCodeDescription.objects.get(code=str(i)).code for i in [1, 2, 10]])

    def test_all_variables(self):
        response_dict = self.get_json('culturalvariable-list')
        self.assertEqual(response_dict['count'], 2)
        for l in ['EA001', 'B002']:
            self.assertTrue(
                self.obj_in_results(CulturalVariable.objects.get(label=l), response_dict))

    def test_filter_source(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'source': Source.objects.get(name='Ethnographic Atlas').id})
        self.assertEqual(response_dict['count'], 1)
        self.assertTrue(
            self.obj_in_results(CulturalVariable.objects.get(label='EA001'), response_dict))
        self.assertFalse(
            self.obj_in_results(CulturalVariable.objects.get(label='B002'), response_dict))

    def test_category1_variables(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'index_categories': [CulturalCategory.objects.get(name='Economy').id]})
        self.assertEqual(response_dict['count'], 2)

    def test_category2_variables(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'index_categories': [CulturalCategory.objects.get(name='Demography').id]})
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['name'],
            CulturalVariable.objects.get(label='EA001').name)
        self.assertFalse(
            self.obj_in_results(CulturalVariable.objects.get(name='Variable 2'), response_dict))

    def test_csv_download(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')
        response = self.get_json(
            'csv_download',
            {'query': json.dumps({'p': [GeographicRegion.objects.get(region_nam='Region1').id]})})
        self.assertIn('Region1'.encode('utf8'), response)

    def test_csv_download_cultural_var(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')
        response = self.get_json(
            'csv_download', 
            {'query': json.dumps({'c': ['%s-%s' % (CulturalCodeDescription.objects.get(code='1').variable.id, CulturalCodeDescription.objects.get(code='1').id)]})})

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
        response = self.get_results(l=[self.get(Language, 1).id])
        for i, assertion in [
            (1, self.assertTrue), (2, self.assertFalse), (3, self.assertFalse)
        ]:
            assertion(self.society_in_results(self.get(Society, i), response))

    def test_find_society_by_var(self):
        response = self.get_results(c=['%s-%s' % (CulturalCodeDescription.objects.get(code='1').variable.id, CulturalCodeDescription.objects.get(code='1').id)])
        for i, assertion in [(1, self.assertTrue), (2, self.assertFalse)]:
            assertion(self.society_in_results(self.get(Society, i), response))

    def test_find_societies_by_var(self):
        serialized_codes = [
            '%s-%s' % (CulturalCodeDescription.objects.get(code=i).variable.id, CulturalCodeDescription.objects.get(code=i).id) for i in ['1', '2']
        ]
        response = self.get_results(c=serialized_codes)
        for i in [1, 2]:
            self.assertTrue(
                self.society_in_results(self.get(Society, i), response))

    def test_find_society_by_name(self):
        response = self.get_results(no_escape=True, name=['Söciety1'])
        for i, assertion in [(1, self.assertTrue), (2, self.assertFalse)]:
            assertion(self.society_in_results(self.get(Society, i), response))

    def test_find_society_by_continuous_var(self):
        response = self.get_results(c=['%s-%s-%s' % (
            CulturalVariable.objects.get(label='B002').id, 0.0, 100)])
        for i, assertion in [(1, self.assertTrue), (2, self.assertFalse)]:
            assertion(self.society_in_results(self.get(Society, i), response))

    def test_find_no_societies(self):
        response = self.get_results(
            c=['%s-%s' % (CulturalCodeDescription.objects.get(code='1').variable.id, CulturalCodeDescription.objects.get(code='10').id)])
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        serialized_vcs = ['%s-%s' % (CulturalCodeDescription.objects.get(code=i).variable.id, CulturalCodeDescription.objects.get(code=i).id) for i in ['1', '2']]
        serialized_lcs = [self.get(Language, i).id for i in [1, 3]]
        response = self.get_results(c=serialized_vcs, l=serialized_lcs)
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[3], response))

    def test_empty_response(self):
        response = self.get_results()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_by_environmental_filter_gt(self):
        response = self.get_results(
            e=[[EnvironmentalVariable.objects.get(name='Rainfall').id,
                'gt', ['1.5']]])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[1], response))

    def test_find_by_environmental_filter_lt(self):
        response = self.get_results(
            e=[[EnvironmentalVariable.objects.get(name='Rainfall').id,
                'lt', ['1.5']]])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_environmental_filter_inrange(self):
        response = self.get_results(
            e=[[EnvironmentalVariable.objects.get(name='Rainfall').id,
                'inrange', ['0.0', '1.5']]])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_environmental_filter_outrange(self):
        response = self.get_results(
            e=[[EnvironmentalVariable.objects.get(name='Rainfall').id,
                'outrange', ['0.0', '3.0']]])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertFalse(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_geographic_region(self):
        """
        This uses a region that contains a single polygon around society 2
        """
        response = self.get_results(p=[GeographicRegion.objects.get(region_nam='Region2').id])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertFalse(self.society_in_results(socs[1], response))
        self.assertTrue(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[3], response))
        self.assertIn('coordinates', response.data['societies'][0]['society']['location'])

    def test_find_by_geographic_region_mpoly(self):
        """
        This uses a region that contains two polygons that should overlap
        societies 1 and 3
        """
        response = self.get_results(p=[GeographicRegion.objects.get(region_nam='Region1').id])
        socs = {i: self.get(Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertTrue(self.society_in_results(socs[3], response))
        self.assertFalse(self.society_in_results(socs[2], response))
