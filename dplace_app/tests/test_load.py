from __future__ import unicode_literals
from collections import defaultdict
import os

from django.test import TestCase

from dplace_app.models import (
    Society, GeographicRegion, Language, LanguageTree, LanguageTreeLabels, LanguageTreeLabelsSequence, ISOCode, CulturalVariable,
)
from dplace_app.load.util import csv_dict_reader, eavar_number_to_label, configure_logging
from dplace_app.load.isocode import load_isocode
from dplace_app.load.society import load_societies, society_locations
from dplace_app.load.values import load_data
from dplace_app.load.variables import load_vars, load_codes
from dplace_app.load.glottocode import xd_to_language
from dplace_app.load.geographic import load_regions
from dplace_app.load.tree import load_trees, tree_names
from dplace_app.load.sources import load_references, get_source


def data_path(fname=None):
    comps = ['data']
    if fname is not None:
        comps.append(fname)
    return os.path.join(os.path.dirname(__file__), *comps)


class LoadTestCase(TestCase):
    """
    Tests loading
    """
    def setUp(self):
        TestCase.setUp(self)
        configure_logging(test=True)

    def get_dict(self, **kw):
        return defaultdict(lambda: '', **kw)

    def test_load_references(self):
        res = load_references(csv_dict_reader(data_path('references.csv')))
        self.assertEqual(res, 2)

    def test_load_vars(self):
        res = load_vars(csv_dict_reader(data_path('variables.csv')))
        self.assertEqual(res, 2)

    def test_load_codes(self):
        CulturalVariable.objects.create(label=eavar_number_to_label(1))
        load_codes(csv_dict_reader(data_path('code_descriptions.csv')))
        # FIXME: assertions!

    def test_load_society_locations(self):
        load_regions(data_path('test_geo.json'))
        load_societies(csv_dict_reader(data_path('societies.csv')))
        society_locations(csv_dict_reader(data_path('society_locations.csv')))

    def test_load_trees(self):
        iso = ISOCode.objects.create(iso_code='abc')
        lang = Language.objects.create(glotto_code='ubyk1235', name='Ubykh', iso_code=iso)
        lang.save()
        load_societies(csv_dict_reader(data_path('societies.csv')))
        society = Society.objects.create(
            ext_id = '455',
            xd_id = 'xd455',
            name = 'test',
            language=lang
        )
        society.save()
        res = load_trees(data_path())
        self.assertEqual(res, 2)
        sequences = tree_names(data_path())
        #labels should be created for the 5 societies in the semitic tree in societies.csv, plus the test society above
        self.assertEqual(sequences, 6)
        
        tree = LanguageTree.objects.filter(name='Abkhaz-Adyge.glotto.trees').first()
        label = LanguageTreeLabels.objects.filter(label='ubyk1235').first()
        self.assertIn(label, tree.taxa.all())
        self.assertIn(society, label.societies.all())
        
        tree = LanguageTree.objects.filter(name='semitic.trees').first()
        labels = LanguageTreeLabels.objects.filter(label='Amharic').first()
        self.assertEqual(tree.taxa.count(), 25)
        self.assertEqual(labels.societies.count(), 3)
        self.assertEqual(labels.societies.all().order_by('-languagetreelabelssequence__fixed_order').first().ext_id, 'Ca7')
        # existing trees are not recreated:
        self.assertEqual(load_trees(data_path()), 0)

    def test_load_regions(self):
        self.assertEqual(load_regions(data_path('test_geo.json')), 2)
        self.assertEqual(
            GeographicRegion.objects.filter(region_nam='Northern Europe').count(), 1)

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
                original_name='Example 1',
                hraf_link='Example (EX1)',
                chirila_link='Example (1)',
                main_focal_year='2016')
        self.assertEqual(load_societies([society('EA'), society('Binford'), society('x')]), 2)

    def test_load_data(self):
        self.assertEqual(load_data([self.get_dict()]), 0)
        self.assertEqual(load_data([self.get_dict(soc_id='notknown')]), 0)
        soc = Society.objects.create(ext_id='socid', name='society')
        soc.save()
        res = load_data([self.get_dict(soc_id='socid')])
        self.assertEqual(res, 0)
        res = load_data([self.get_dict(soc_id='socid', Dataset='Binford')])
        self.assertEqual(res, 0)
        load_vars([self.get_dict(Dataset='Binford', VarId='5', VarType='Ordinal')])
        res = load_data([self.get_dict(soc_id='socid', Dataset='Binford', VarId='5')])
        self.assertEqual(res, 1)

    def test_environmental(self):
        from dplace_app.load.environmental import (
            load_environmental_var, load_environmental,
        )
        res = load_environmental([self.get_dict(Dataset='EA')])
        self.assertEqual(res, 0)
        res = load_environmental_var(csv_dict_reader(data_path('envvariables.csv')))
        self.assertEqual(res, 3)
        row_dict = self.get_dict(
            dataset='EA',
            soc_id='EA12',
            xd_id='xd1',
            soc_name='Example EA Society',
            alternate_names='Example',
            main_focal_year='2016')
        load_societies([row_dict])
        res = load_environmental([self.get_dict(**{
            'Dataset': 'EA',
            'soc_id': 'EA12',
            'variable': 'AnnualMeanTemperature',
            'value': 1,
            'comment': "Comment"
        })])
        self.assertEqual(res, 1)
    
    def test_get_source_raises_ValueError(self):
        with self.assertRaises(ValueError):
            get_source(source='personal communication')
