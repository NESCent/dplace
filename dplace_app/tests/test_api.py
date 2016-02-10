from __future__ import unicode_literals
import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from dplace_app.serializers import (
    GeographicRegionSerializer, LanguageSerializer, CulturalCodeDescriptionSerializer,
)
from dplace_app import models


class Test(APITestCase):
    """Tests rest-framework API"""
    _data = {}

    def get_json(self, urlname, *args, **kw):
        kw.setdefault('format', 'json')
        reverse_args = kw.pop('reverse_args', [])
        response = self.client.get(
            reverse(urlname, args=reverse_args), *args, **kw
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return json.loads(response.content)

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
        region1 = self.set(
            models.GeographicRegion, 1,
            level_2_re='1', count=1, region_nam='Region1', tdwg_code=0)
        region2 = self.set(
            models.GeographicRegion, 2,
            level_2_re='2', count=1, region_nam='Region2', tdwg_code=1)
        ec1 = self.set(models.EnvironmentalCategory, 1, name='Climate')
        ec2 = self.set(models.EnvironmentalCategory, 2, name='Ecology')
        for i, (name, cat, units, info) in enumerate([
            ('Rainfall', ec1, 'mm', 'Precipitation'),
            ('Temperature', ec1, 'C', 'Temperature'),
            ('Ecology1', ec2, '', ''),
        ]):
            self.set(
                models.EnvironmentalVariable, i + 1,
                name=name, category=cat, units=units, codebook_info=info)

        source_ea = self.set(
            models.Source, 'ea',
            year='2016',
            author='Simon Greenhill',
            reference='Greenhill (2016). Title.',
            name='EA Test Dataset')
        source_binford = self.set(
            models.Source, 'binford',
            year='2016',
            author='Russell Gray',
            reference='Gray (2016). Title.',
            name='BF Test Dataset')

        category1 = self.set(models.CulturalCategory, 1, name='Economy')
        category2 = self.set(models.CulturalCategory, 2, name='Demography')

        variable1 = self.set(
            models.CulturalVariable, 1,
            label='EA001',
            name='Variable 1',
            source=source_ea,
            codebook_info='Variable 1',
            data_type='Categorical')
        variable2 = self.set(
            models.CulturalVariable, 2,
            label='B002',
            name='Variable 2',
            source=source_binford,
            codebook_info='Variable 2',
            data_type='Continuous')
        variable1.index_categories.add(category1, category2)
        variable2.index_categories.add(category2)

        code1 = self.set(
            models.CulturalCodeDescription, 1,
            variable=variable1, code='1', description='Code 1')
        self.set(
            models.CulturalCodeDescription, 10,
            variable=variable1, code='10', description='Code 10')
        code2 = self.set(
            models.CulturalCodeDescription, 2,
            variable=variable1, code='2', description='Code 2')

        family1 = self.set(models.LanguageFamily, 1, name='family1')
        family2 = self.set(models.LanguageFamily, 2, name='family2')
        iso_code = self.set(models.ISOCode, 1, iso_code='abc')
        language1 = self.set(
            models.Language, 1,
            name='language1', family=family1, glotto_code='aaaa1234', iso_code=iso_code)
        language2 = self.set(
            models.Language, 2,
            name='language2', family=family2, glotto_code='dddd1234')
        language3 = self.set(
            models.Language, 3,
            name='language3', family=family2, glotto_code='cccc1234', iso_code=iso_code)
        tree1 = self.set(
            models.LanguageTree, 1,
            newick_string='((aaaa1234:1,abc:1,abun1254:1)abun1252:1);',
            name='tree',
            source=source_ea)
        tree1.languages.add(language1)
        tree2 = self.set(
            models.LanguageTree, 2,
            newick_string='((aaaa1234:1,abc:1,abun1254:1)abun1252:1);',
            name='tree.glotto.trees',
            source=source_ea)
        tree2.languages.add(language1)

        society1 = self.set(
            models.Society, 1,
            ext_id='society1',
            xd_id='xd1',
            name='Society1',
            region=region1,
            source=source_ea,
            language=language1,
            focal_year='2016',
            alternate_names='Society 1')
        society2 = self.set(
            models.Society, 2,
            ext_id='society2',
            xd_id='xd2',
            region=region2,
            name='Society2',
            source=source_ea,
            language=language2)
        # Society 3 has the same language characteristics as society 1
        # but different EA Vars
        society3 = self.set(
            models.Society, 3,
            ext_id='society3',
            xd_id='xd1',
            region=region1,
            name='Society3',
            source=source_ea,
            language=language3)

        self.set(
            models.CulturalValue, 1,
            variable=variable1,
            society=society1,
            coded_value='1',
            code=code1,
            source=source_ea)
        models.CulturalValue.objects.create(
            variable=variable1,
            society=society2,
            coded_value='2',
            code=code2,
            source=source_ea)

        # Setup environmentals
        environmental1 = self.set(
            models.Environmental, 1,
            society=society1,
            source=source_ea,
            iso_code=iso_code)
        environmental2 = self.set(
            models.Environmental, 2,
            society=society2,
            source=source_ea,
            iso_code=iso_code)

        env_var = self.get(models.EnvironmentalVariable, 1)
        self.set(
            models.EnvironmentalValue, 1,
            variable=env_var,
            value=1.0, source=source_ea,
            environmental=environmental1)
        self.set(
            models.EnvironmentalValue, 2,
            variable=env_var,
            value=2.0, source=source_ea,
            environmental=environmental2)

    def test_api_culturalcategory(self):
        res = self.get_json(
            'culturalcategory-detail',
            reverse_args=[self.get(models.CulturalCategory, 1).id])
        self.assertIsInstance(res['index_variables'][0], dict)

    def test_api_culturalvariable(self):
        res = self.get_json(
            'culturalvariable-detail',
            reverse_args=[self.get(models.CulturalVariable, 1).id])
        self.assertIsInstance(res['index_categories'][0], dict)

    def test_zip_legends(self):
        response = self.client.post(reverse('zip_legends'))
        self.assertIn('attachment', response['Content-Disposition'])

    def test_get_categories(self):
        response = self.get_json('get_categories', {'query': json.dumps({})})
        self.assertIsInstance(response, list)
        response = self.get_json(
            'get_categories',
            {'query': json.dumps(dict(source=self.get(models.Source, 'ea').id))})
        self.assertIsInstance(response, list)

    def test_min_and_max(self):
        response = self.get_json(
            'min_and_max',
            {'query': json.dumps(
                dict(environmental_id=self.get(models.EnvironmentalVariable, 1).id))})
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
            {'query': json.dumps(dict(bf_id=self.get(models.CulturalVariable, 2).id))})
        self.assertIsInstance(response, list)

    def test_geo_api(self):
        response = self.client.get(reverse('geographicregion-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            response.data['results'][0]['region_nam'],
            self.get(models.GeographicRegion, 1).region_nam)

    def test_isocode_api(self):
        response_dict = self.get_json('isocode-list')
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['iso_code'], self.get(models.ISOCode, 1).iso_code)

    def test_all_languages(self):
        response_dict = self.get_json('language-list')
        self.assertEqual(response_dict['count'], 3)
        for i in [1, 2, 3]:
            self.assertTrue(
                self.obj_in_results(self.get(models.Language, i), response_dict))

    def test_family2_languages(self):
        response_dict = self.get_json(
            'language-list',
            {'family': self.get(models.LanguageFamily, 2).id})
        self.assertEqual(response_dict['count'], 2)
        self.assertFalse(self.obj_in_results(self.get(models.Language, 1), response_dict))

    def test_all_environmental_variables(self):
        response_dict = self.get_json('environmentalvariable-list')
        self.assertEqual(response_dict['count'], 3)
        for i in [1, 2, 3]:
            env_var = self.get(models.EnvironmentalVariable, i)
            self.assertTrue(self.obj_in_results(env_var, response_dict))

    def test_env_category1_variables(self):
        response_dict = self.get_json(
            'environmentalvariable-list',
            {'category': self.get(models.EnvironmentalCategory, 1).id})
        for i, assertion in [
            (1, self.assertTrue), (2, self.assertTrue), (3, self.assertFalse)
        ]:
            env_var = self.get(models.EnvironmentalVariable, i)
            assertion(self.obj_in_results(env_var, response_dict))

    def test_code_description_order(self):
        """
        Make sure 2 comes before 10
        """
        response_dict = self.get_json(
            'culturalcodedescription-list',
            {'variable': self.get(models.CulturalVariable, 1).id})
        self.assertEqual(
            [res['code'] for res in response_dict['results']],
            [self.get(models.CulturalCodeDescription, i).code for i in [1, 2, 10]])

    def test_all_variables(self):
        response_dict = self.get_json('culturalvariable-list')
        self.assertEqual(response_dict['count'], 2)
        for i in [1, 2]:
            self.assertTrue(
                self.obj_in_results(self.get(models.CulturalVariable, i), response_dict))

    def test_filter_source(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'source': self.get(models.Source, 'ea').id})
        self.assertEqual(response_dict['count'], 1)
        self.assertTrue(
            self.obj_in_results(self.get(models.CulturalVariable, 1), response_dict))
        self.assertFalse(
            self.obj_in_results(self.get(models.CulturalVariable, 2), response_dict))

    def test_category1_variables(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'index_categories': [self.get(models.CulturalCategory, 1).id]})
        self.assertEqual(response_dict['count'], 1)
        self.assertEqual(
            response_dict['results'][0]['name'],
            self.get(models.CulturalVariable, 1).name)
        self.assertFalse(
            self.obj_in_results(self.get(models.CulturalVariable, 2), response_dict))

    def test_category2_variables(self):
        response_dict = self.get_json(
            'culturalvariable-list',
            {'index_categories': [self.get(models.CulturalCategory, 2).id]})
        self.assertEqual(response_dict['count'], 2)
        for i in [1, 2]:
            self.assertTrue(
                self.obj_in_results(self.get(models.CulturalVariable, i), response_dict))

    def test_csv_download(self):
        response = self.client.get(reverse('csv_download'))
        self.assertEqual(response.content.split()[0], '"Research')

        response = self.get_results(
            urlname='csv_download',
            geographic_regions=[
                GeographicRegionSerializer(self.get(models.GeographicRegion, 1)).data])
        self.assertIn('Region1', response.content)

    #
    # find societies:
    #
    def get_results(self, urlname='find_societies', **data):
        return self.client.post(reverse(urlname), data or {}, format='json')

    def society_in_results(self, society, response):
        return society.id in [x['society']['id'] for x in response.data['societies']]

    def test_find_societies_by_language(self):
        # Find the societies that use language1
        classifications = LanguageSerializer([self.get(models.Language, 1)], many=True)
        response = self.get_results(language_classifications=classifications.data)
        for i, assertion in [
            (1, self.assertTrue), (2, self.assertFalse), (3, self.assertFalse)
        ]:
            assertion(self.society_in_results(self.get(models.Society, i), response))

    def test_find_society_by_var(self):
        response = self.get_results(variable_codes=CulturalCodeDescriptionSerializer(
            [self.get(models.CulturalCodeDescription, 1)], many=True).data)
        for i, assertion in [(1, self.assertTrue), (2, self.assertFalse)]:
            assertion(self.society_in_results(self.get(models.Society, i), response))

    def test_find_societies_by_var(self):
        serialized_codes = CulturalCodeDescriptionSerializer(
            [self.get(models.CulturalCodeDescription, i) for i in [1, 2]], many=True).data
        response = self.get_results(variable_codes=serialized_codes)
        for i in [1, 2]:
            self.assertTrue(
                self.society_in_results(self.get(models.Society, i), response))

    def test_find_no_societies(self):
        response = self.get_results(
            variable_codes=CulturalCodeDescriptionSerializer(
                [self.get(models.CulturalCodeDescription, 10)], many=True).data)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_society_by_language_and_var(self):
        # Search for societies with language 1 and language 3
        # Coded with variable codes 1 and 2
        # this should return only 1 and not 2 or 3
        # This tests that results should be intersection (AND), not union (OR)
        # Society 3 is not coded for any variables, so it should not appear in the list.
        serialized_vcs = CulturalCodeDescriptionSerializer(
            [self.get(models.CulturalCodeDescription, i) for i in [1, 2]], many=True).data
        serialized_lcs = LanguageSerializer(
            [self.get(models.Language, i) for i in [1, 3]], many=True).data
        response = self.get_results(
            variable_codes=serialized_vcs,
            language_classifications=serialized_lcs)
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[3], response))

    def test_empty_response(self):
        response = self.get_results()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['societies']), 0)

    def test_find_by_environmental_filter_gt(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.get(models.EnvironmentalVariable, 1).id),
                 'operator': 'gt',
                 'params': ['1.5']}])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[1], response))

    def test_find_by_environmental_filter_lt(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.get(models.EnvironmentalVariable, 1).id),
                 'operator': 'lt',
                 'params': ['1.5']}])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_environmental_filter_inrange(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.get(models.EnvironmentalVariable, 1).id),
                 'operator': 'inrange',
                 'params': ['0.0', '1.5']}])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_environmental_filter_outrange(self):
        response = self.get_results(
            environmental_filters=[
                {'id': str(self.get(models.EnvironmentalVariable, 1).id),
                 'operator': 'outrange',
                 'params': ['0.0', '3.0']}])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertFalse(self.society_in_results(socs[1], response))
        self.assertFalse(self.society_in_results(socs[2], response))

    def test_find_by_geographic_region(self):
        """
        This uses a region that contains a single polygon around society 2
        """
        response = self.get_results(
            geographic_regions=[
                GeographicRegionSerializer(self.get(models.GeographicRegion, 2)).data])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertFalse(self.society_in_results(socs[1], response))
        self.assertTrue(self.society_in_results(socs[2], response))
        self.assertFalse(self.society_in_results(socs[3], response))
        self.assertIn('coordinates', response.data['societies'][0]['society']['location'])

    def test_find_by_geographic_region_mpoly(self):
        """
        This uses a region that contains two polygons that should overlap
        societies 1 and 3
        """
        response = self.get_results(
            geographic_regions=[
                GeographicRegionSerializer(self.get(models.GeographicRegion, 1)).data])
        socs = {i: self.get(models.Society, i) for i in [1, 2, 3]}
        self.assertTrue(self.society_in_results(socs[1], response))
        self.assertTrue(self.society_in_results(socs[3], response))
        self.assertFalse(self.society_in_results(socs[2], response))
