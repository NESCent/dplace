# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Language.family'
        db.delete_column(u'dplace_app_language', 'family_id')

        # Deleting field 'Language.classification'
        db.delete_column(u'dplace_app_language', 'classification_id')

        # Deleting field 'Language.class2'
        db.delete_column(u'dplace_app_language', 'class2_id')

        # Deleting field 'Language.class3'
        db.delete_column(u'dplace_app_language', 'class3_id')

        # Deleting field 'Language.class1'
        db.delete_column(u'dplace_app_language', 'class1_id')

        # Adding field 'Language.society'
        db.add_column(u'dplace_app_language', 'society',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', null=True, to=orm['dplace_app.Society']),
                      keep_default=False)

        # Adding field 'LanguageClassification.scheme'
        db.add_column(u'dplace_app_languageclassification', 'scheme',
                      self.gf('django.db.models.fields.CharField')(default='E', max_length=1),
                      keep_default=False)

        # Adding field 'LanguageClassification.language'
        db.add_column(u'dplace_app_languageclassification', 'language',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.Language'], null=True),
                      keep_default=False)

        # Adding field 'LanguageClassification.family'
        db.add_column(u'dplace_app_languageclassification', 'family',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', null=True, to=orm['dplace_app.LanguageFamily']),
                      keep_default=False)

        # Adding field 'LanguageClassification.class_family'
        db.add_column(u'dplace_app_languageclassification', 'class_family',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages1', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Adding field 'LanguageClassification.class_subfamily'
        db.add_column(u'dplace_app_languageclassification', 'class_subfamily',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages2', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Adding field 'LanguageClassification.class_subsubfamily'
        db.add_column(u'dplace_app_languageclassification', 'class_subsubfamily',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages3', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Adding index on 'LanguageClassification', fields ['class_family', 'class_subfamily', 'class_subsubfamily']
        db.create_index(u'dplace_app_languageclassification', ['class_family_id', 'class_subfamily_id', 'class_subsubfamily_id'])


    def backwards(self, orm):
        # Removing index on 'LanguageClassification', fields ['class_family', 'class_subfamily', 'class_subsubfamily']
        db.delete_index(u'dplace_app_languageclassification', ['class_family_id', 'class_subfamily_id', 'class_subsubfamily_id'])

        # Adding field 'Language.family'
        db.add_column(u'dplace_app_language', 'family',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', null=True, to=orm['dplace_app.LanguageFamily']),
                      keep_default=False)

        # Adding field 'Language.classification'
        db.add_column(u'dplace_app_language', 'classification',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', null=True, to=orm['dplace_app.LanguageClassification']),
                      keep_default=False)

        # Adding field 'Language.class2'
        db.add_column(u'dplace_app_language', 'class2',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages2', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Adding field 'Language.class3'
        db.add_column(u'dplace_app_language', 'class3',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages3', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Adding field 'Language.class1'
        db.add_column(u'dplace_app_language', 'class1',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages1', null=True, to=orm['dplace_app.LanguageClass']),
                      keep_default=False)

        # Deleting field 'Language.society'
        db.delete_column(u'dplace_app_language', 'society_id')

        # Deleting field 'LanguageClassification.scheme'
        db.delete_column(u'dplace_app_languageclassification', 'scheme')

        # Deleting field 'LanguageClassification.language'
        db.delete_column(u'dplace_app_languageclassification', 'language_id')

        # Deleting field 'LanguageClassification.family'
        db.delete_column(u'dplace_app_languageclassification', 'family_id')

        # Deleting field 'LanguageClassification.class_family'
        db.delete_column(u'dplace_app_languageclassification', 'class_family_id')

        # Deleting field 'LanguageClassification.class_subfamily'
        db.delete_column(u'dplace_app_languageclassification', 'class_subfamily_id')

        # Deleting field 'LanguageClassification.class_subsubfamily'
        db.delete_column(u'dplace_app_languageclassification', 'class_subsubfamily_id')


    models = {
        u'dplace_app.eavariablecodedescription': {
            'Meta': {'ordering': "('number', 'code')", 'object_name': 'EAVariableCodeDescription'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'codes'", 'to': u"orm['dplace_app.EAVariableDescription']"})
        },
        u'dplace_app.eavariabledescription': {
            'Meta': {'ordering': "('number',)", 'object_name': 'EAVariableDescription'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        u'dplace_app.eavariablevalue': {
            'Meta': {'ordering': "('society', 'code')", 'object_name': 'EAVariableValue'},
            'code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.EAVariableCodeDescription']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.Society']"})
        },
        u'dplace_app.environmental': {
            'Meta': {'object_name': 'Environmental'},
            'actual_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'amphibian_diversity': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'annual_mean_precipitation': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'annual_mean_temperature': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'annual_precipitation_variance': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'annual_temperature_variance': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'bird_diversity': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'elevation': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'mammal_diversity': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mean_growing_season_duration': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'net_primary_productivity': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'plant_diversity': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'precipitation_constancy': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'precipitation_contingency': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'precipitation_predictability': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'reported_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'slope': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.Society']"}),
            'temperature_constancy': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'temperature_contingency': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'temperature_predictability': ('django.db.models.fields.FloatField', [], {'null': 'True'})
        },
        u'dplace_app.isocode': {
            'Meta': {'object_name': 'ISOCode'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {})
        },
        u'dplace_app.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'unique': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'null': 'True', 'to': u"orm['dplace_app.Society']"})
        },
        u'dplace_app.languageclass': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'LanguageClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'dplace_app.languageclassification': {
            'Meta': {'object_name': 'LanguageClassification', 'index_together': "[['class_family', 'class_subfamily', 'class_subsubfamily']]"},
            'class_family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages1'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class_subfamily': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages2'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class_subsubfamily': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages3'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'null': 'True', 'to': u"orm['dplace_app.LanguageFamily']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Language']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'E'", 'max_length': '1'})
        },
        u'dplace_app.languagefamily': {
            'Meta': {'object_name': 'LanguageFamily'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'})
        },
        u'dplace_app.society': {
            'Meta': {'object_name': 'Society'},
            'ext_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        }
    }

    complete_apps = ['dplace_app']