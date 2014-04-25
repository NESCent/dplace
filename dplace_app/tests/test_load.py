__author__ = 'dan'
from dplace_app.load.isocode import load_isocode, load_iso_lat_long
from dplace_app.load.society_binford import load_bf_society
from dplace_app.load.society_ea import load_ea_society
from django.test import TestCase

class LoadISOCodeTestCase(TestCase):
    '''
    Tests loading
    '''
    def test_load_isocode(self):
        row_dict = {'ISO 693-3 code': 'abc'}
        isocode = load_isocode(row_dict)
        self.assertIsNotNone(isocode, 'Unable to load an iso code with 3 characters')
    def test_isocode_too_long(self):
        row_dict = {'ISO 693-3 code': 'abcd'}
        isocode = load_isocode(row_dict)
        self.assertIsNone(isocode, 'Should not load an isocode with 4 characters')
    def test_isocode_not_present(self):
        row_dict = {'foo':'bar'}
        isocode = load_isocode(row_dict)
        self.assertIsNone(isocode, 'Should not load an isocode without iso code')
    def load_iso_lat_long(self):
        row_dict = {'ISO':'abc','LMP_LON': 30.43, 'LMP_LAT': 21.44}
        isocode = load_isocode(row_dict)
        self.assertIsNotNone(isocode, 'Unable to load code before attaching lat/long')
        isocode = load_iso_lat_long(row_dict)
        self.assertIsNotNone(isocode, 'Unable to attach lat/long to iso code')
    def test_load_ea_society(self):
        row_dict = {
            'ID': 'EA12',
            'Society_name_EA': 'Example EA Society',
            'ISO693_3': 'abc',
            'LangNam': 'Language, Test',
        }
        iso_code = load_isocode({'ISO': 'abc'}) # Make sure iso code exists
        self.assertIsNotNone(iso_code, 'Did not create iso_code')
        society = load_ea_society(row_dict)
        self.assertIsNotNone(society, 'unable to load society')
        self.assertIsNotNone(society.iso_code, 'society has no linked iso code')
        self.assertEqual(society.source, 'EA', 'Society source should be EA')
        # Not testing language creation here
        self.assertIsNone(society.language, 'society should have no language')
    def test_load_bf_society(self):
        row_dict = {
            'ID': 'BF34',
            'STANDARD SOCIETY NAME Binford': 'Example Binford Society',
            'ISO693_3': 'def',
            'LangNam': 'Language2, Test',
            }

        iso_code = load_isocode({'ISO': 'def'}) # Make sure iso code exists
        self.assertIsNotNone(iso_code, 'Did not create iso_code')
        society = load_bf_society(row_dict)
        self.assertIsNotNone(society, 'unable to load society')
        self.assertIsNotNone(society.iso_code, 'society has no linked iso code')
        self.assertEqual(society.source, 'Binford', 'Society source should be Binford')
        # Not testing language creation here
        self.assertIsNone(society.language, 'society should have no language')


