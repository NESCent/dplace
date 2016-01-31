from __future__ import unicode_literals
from collections import defaultdict

from django.test import TestCase

from dplace_app.load.isocode import load_isocode
from dplace_app.load.society_binford import load_bf_society
from dplace_app.load.society_ea import load_ea_society
from dplace_app.load.values import load_data
from dplace_app.load.variables import load_vars


class LoadISOCodeTestCase(TestCase):
    '''
    Tests loading
    '''
    def get_dict(self, **kw):
        return defaultdict(lambda: '', **kw)

    def test_load_isocode(self):
        isocode = load_isocode({'ISO 693-3 code': 'abc'})
        self.assertIsNotNone(isocode, 'Unable to load an iso code with 3 characters')

    def test_isocode_too_long(self):
        isocode = load_isocode({'ISO 693-3 code': 'abcd'})
        self.assertIsNone(isocode, 'Should not load an isocode with 4 characters')

    def test_isocode_not_present(self):
        isocode = load_isocode({'foo': 'bar'})
        self.assertIsNone(isocode, 'Should not load an isocode without iso code')

    def test_load_ea_society(self):
        row_dict = self.get_dict(
            dataset='EA',
            soc_id='EA12',
            xd_id='xd1',
            soc_name='Example EA Society',
            alternate_names='Example',
            main_focal_year='2016')
        society = load_ea_society(row_dict)
        self.assertIsNotNone(society, 'unable to load society')
        self.assertEqual(society.source.author, 'Murdock et al.', '! Murdock et al.')

    def test_load_bf_society(self):
        row_dict = self.get_dict(**{
            'soc_id': 'socid',
            'soc_name': 'socname',
            'xd_id': 'xdid',
            'ID': 'BF34',
            'STANDARD SOCIETY NAME Binford': 'Example Binford Society',
            'ISO693_3': 'def',
            'LangNam': 'Language2, Test'
        })
        society = load_bf_society(row_dict)
        self.assertIsNotNone(society, 'unable to load society')
        self.assertEqual(society.source.author, 'Binford', '! Binford')

    def test_load_data(self):
        self.assertEqual(load_data([self.get_dict()]), 0)
        self.assertEqual(load_data([self.get_dict(soc_id='notknown')]), 0)
        row_dict = self.get_dict(**{
            'soc_id': 'socid',
            'soc_name': 'socname',
            'xd_id': 'xdid',
            'ID': 'BF34',
            'STANDARD SOCIETY NAME Binford': 'Example Binford Society',
            'ISO693_3': 'def',
            'LangNam': 'Language2, Test'
        })
        load_bf_society(row_dict)
        res = load_data([self.get_dict(soc_id='socid')])
        self.assertEqual(res, 0)
        res = load_data([self.get_dict(soc_id='socid', Dataset='LRB')])
        self.assertEqual(res, 0)
        load_vars(self.get_dict(Dataset='LRB', VarId='5'))
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
        load_ea_society(row_dict)
        res = load_environmental([self.get_dict(**{
            'Source': 'EA',
            'ID': 'EA12',
            'Orig.longitude': 1,
            'Orig.latitude': 1,
            'longitude': 1,
            'latitude': 1,
        })])
        self.assertEqual(res, 1)
