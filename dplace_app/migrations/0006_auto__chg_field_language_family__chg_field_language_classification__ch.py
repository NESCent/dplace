# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Language.family'
        db.alter_column(u'dplace_app_language', 'family_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dplace_app.LanguageFamily']))

        # Changing field 'Language.classification'
        db.alter_column(u'dplace_app_language', 'classification_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dplace_app.LanguageClassification']))

        # Changing field 'Language.class1'
        db.alter_column(u'dplace_app_language', 'class1_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dplace_app.LanguageClass']))

        # Changing field 'Language.class2'
        db.alter_column(u'dplace_app_language', 'class2_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dplace_app.LanguageClass']))

        # Changing field 'Language.class3'
        db.alter_column(u'dplace_app_language', 'class3_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['dplace_app.LanguageClass']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Language.family'
        raise RuntimeError("Cannot reverse this migration. 'Language.family' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Language.family'
        db.alter_column(u'dplace_app_language', 'family_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.LanguageFamily']))

        # User chose to not deal with backwards NULL issues for 'Language.classification'
        raise RuntimeError("Cannot reverse this migration. 'Language.classification' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Language.classification'
        db.alter_column(u'dplace_app_language', 'classification_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.LanguageClassification']))

        # User chose to not deal with backwards NULL issues for 'Language.class1'
        raise RuntimeError("Cannot reverse this migration. 'Language.class1' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Language.class1'
        db.alter_column(u'dplace_app_language', 'class1_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.LanguageClass']))

        # User chose to not deal with backwards NULL issues for 'Language.class2'
        raise RuntimeError("Cannot reverse this migration. 'Language.class2' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Language.class2'
        db.alter_column(u'dplace_app_language', 'class2_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.LanguageClass']))

        # User chose to not deal with backwards NULL issues for 'Language.class3'
        raise RuntimeError("Cannot reverse this migration. 'Language.class3' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Language.class3'
        db.alter_column(u'dplace_app_language', 'class3_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.LanguageClass']))

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
            'class1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages1'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages2'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages3'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClassification']"}),
            'family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'null': 'True', 'to': u"orm['dplace_app.LanguageFamily']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'unique': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'dplace_app.languageclass': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'LanguageClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'dplace_app.languageclassification': {
            'Meta': {'object_name': 'LanguageClassification'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'})
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