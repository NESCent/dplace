# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'EAVariableCodeDescription.n'
        db.add_column(u'dplace_app_eavariablecodedescription', 'n',
                      self.gf('django.db.models.fields.IntegerField')(default=0, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'EAVariableCodeDescription.n'
        db.delete_column(u'dplace_app_eavariablecodedescription', 'n')


    models = {
        u'dplace_app.eavariablecodedescription': {
            'Meta': {'ordering': "('variable', 'code_number', 'code')", 'object_name': 'EAVariableCodeDescription'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '20', 'db_index': 'True'}),
            'code_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'codes'", 'to': u"orm['dplace_app.EAVariableDescription']"})
        },
        u'dplace_app.eavariablecodedvalue': {
            'Meta': {'ordering': "('variable', 'coded_value')", 'object_name': 'EAVariableCodedValue', 'index_together': "[['variable', 'society'], ['variable', 'coded_value'], ['variable', 'code'], ['society', 'coded_value'], ['society', 'code']]"},
            'code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.EAVariableCodeDescription']", 'null': 'True'}),
            'coded_value': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '20', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Society']", 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.EAVariableDescription']"})
        },
        u'dplace_app.eavariabledescription': {
            'Meta': {'ordering': "('number',)", 'object_name': 'EAVariableDescription'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '200', 'db_index': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'})
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['dplace_app.LanguageClass']", 'null': 'True'})
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