from __future__ import unicode_literals
from collections import defaultdict

from django.test import TestCase

from dplace_app.models import Society
from dplace_app.load.isocode import load_isocode
from dplace_app.load.society import load_societies
from dplace_app.load.values import load_data
from dplace_app.load.variables import load_vars
from dplace_app.load.glottocode import xd_to_language


class LoadTestCase(TestCase):
    '''
    Tests loading
    '''
    def get_dict(self, **kw):
        return defaultdict(lambda: '', **kw)

    def test_load_language(self):
        soc = Society.objects.create(ext_id='socid', xd_id='socid', name='society')
        soc.save()
        res = xd_to_language(
            [self.get_dict(xd_id='socid', DialectLanguageGlottocode='none1234')],
            [self.get_dict(id='abcd1234', name='name', iso_code='iso')])
        self.assertEqual(res, 0)
        res = xd_to_language(
            [self.get_dict(xd_id='socid', DialectLanguageGlottocode='abcd1234')],
            [self.get_dict(id='abcd1234', name='name', iso_code='iso')])
        self.assertEqual(res, 1)

    def test_load_isocode(self):
        isocode = load_isocode({'ISO 693-3 code': 'abc'})
        self.assertIsNotNone(isocode, 'Unable to load an iso code with 3 characters')

    def test_isocode_too_long(self):
        isocode = load_isocode({'ISO 693-3 code': 'abcd'})
        self.assertIsNone(isocode, 'Should not load an isocode with 4 characters')

    def test_isocode_not_present(self):
        isocode = load_isocode({'foo': 'bar'})
        self.assertIsNone(isocode, 'Should not load an isocode without iso code')

    def test_load_society(self):
        def society(dataset):
            return self.get_dict(
                dataset=dataset,
                soc_id='EA12' + dataset,
                xd_id='xd1',
                soc_name='Example Society',
                alternate_names='Example',
                main_focal_year='2016')
        self.assertEqual(load_societies([society('EA'), society('LRB'), society('x')]), 2)

    def test_load_data(self):
        self.assertEqual(load_data([self.get_dict()]), 0)
        self.assertEqual(load_data([self.get_dict(soc_id='notknown')]), 0)
        soc = Society.objects.create(ext_id='socid', name='society')
        soc.save()
        res = load_data([self.get_dict(soc_id='socid')])
        self.assertEqual(res, 0)
        res = load_data([self.get_dict(soc_id='socid', Dataset='LRB')])
        self.assertEqual(res, 0)
        load_vars([self.get_dict(Dataset='LRB', VarId='5')])
        res = load_data([self.get_dict(soc_id='socid', Dataset='LRB', VarId='5')])
        self.assertEqual(res, 1)

    def test_environmental(self):
        from dplace_app.load.environmental import (
            create_environmental_variables, load_environmental,
        )

        res = load_environmental([self.get_dict(Source='EA')])
        self.assertEqual(res, 0)
        row_dict = self.get_dict(
            dataset='EA',
            soc_id='EA12',
            xd_id='xd1',
            soc_name='Example EA Society',
            alternate_names='Example',
            main_focal_year='2016')
        load_societies([row_dict])
        res = load_environmental([self.get_dict(**{
            'Source': 'EA',
            'ID': 'EA12',
            'Orig.longitude': 1,
            'Orig.latitude': 1,
            'longitude': 1,
            'latitude': 1,
        })])
        self.assertEqual(res, 1)
