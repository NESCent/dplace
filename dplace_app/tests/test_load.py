# coding: utf8
from __future__ import unicode_literals, print_function, division
from unittest import TestCase

import attr


class Tests(TestCase):
    def test_Variable(self):
        from dplace_app.load import Variable

        def kwargs(**kw):
            for field in attr.fields(Variable):
                if field.default == attr.NOTHING:
                    kw.setdefault(field.name, '')
            return kw

        with self.assertRaises(ValueError):
            Variable(**kwargs())

        self.assertEqual(
            Variable(**kwargs(category='ab, cd', type='Ordinal')).category, ['Ab', 'Cd'])
