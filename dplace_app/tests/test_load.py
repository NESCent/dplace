
__author__ = 'dan'
from collections import defaultdict
from dplace_app.load.isocode import load_isocode
from dplace_app.load.society_binford import load_bf_society
from dplace_app.load.society_ea import load_ea_society
#from dplace_app.load.language import load_lang
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
    def test_load_ea_society(self):
        row_dict = defaultdict(
            lambda: '',
            **{
            'ID': 'EA12',
            'Society_name_EA': 'Example EA Society',
            'ISO693_3': 'abc',
            'LangNam': 'Language, Test',
        })
        iso_code = load_isocode({'ISO': 'abc'}) # Make sure iso code exists
        self.assertIsNotNone(iso_code, 'Did not create iso_code')
        society = load_ea_society(row_dict)
        #self.assertIsNotNone(society, 'unable to load society')
        #self.assertIsNotNone(society.iso_code, 'society has no linked iso code')
        #self.assertEqual(society.source.author, 'Murdock et al.', 'Society source should be Murdock et al.')
        # Not testing language creation here
        #self.assertIsNone(society.language, 'society should have no language')
    def test_load_bf_society(self):
        row_dict = defaultdict(
            lambda: '',
            **{'soc_id': 'socid',
            'soc_name': 'socname',
            'xd_id': 'xdid',
            'ID': 'BF34',
            'STANDARD SOCIETY NAME Binford': 'Example Binford Society',
            'ISO693_3': 'def',
            'LangNam': 'Language2, Test'})

        iso_code = load_isocode({'ISO': 'def'}) # Make sure iso code exists
        self.assertIsNotNone(iso_code, 'Did not create iso_code')
        society = load_bf_society(row_dict)
        # FIXME: the following assertions need to be fixed!
        #self.assertIsNotNone(society, 'unable to load society')
        #self.assertIsNotNone(society.iso_code, 'society has no linked iso code')
        #self.assertEqual(society.source.author, 'Binford', 'Society source should be Binford')
        # Not testing language creation here
        #self.assertIsNone(society.language, 'society should have no language')
        
    # FIXME: old code, will not work as load_lang relies on LanguageClass and LanguageClassification
    #def test_load_language(self):
    #    row_dict = {
    #        'ISO 693-3 code': 'acv',
    #        'Language name': 'Achumawi',
    #        'FAMILY-REVISED': 'Palaihnihan',
    #        'Class2': '',
    #        'Class3': '',
    #        'Ethnologue Classification (unrevised)': 'Palaihnihan',
    #    }
    #    iso_code = load_isocode({'ISO': 'acv'}) # Make sure iso code exists
    #    self.assertIsNotNone(iso_code, 'Did not create iso_code')
    #    language = load_lang(row_dict)
    #    self.assertIsNotNone(language, 'unable to load language')
    #    self.assertEqual(row_dict['Language name'], language.name, 'Language did not have correct name')
    #    classification = language.languageclassification_set.first()
    #    self.assertEqual(row_dict['FAMILY-REVISED'], classification.class_family.name, 'Language did not have correct family name')


