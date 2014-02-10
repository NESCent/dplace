# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table(u'dplace_app_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('iso_code', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', to=orm['dplace_app.ISOCode'])),
            ('family', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', to=orm['dplace_app.LanguageFamily'])),
            ('classification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages', to=orm['dplace_app.LanguageClassification'])),
            ('class1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages1', to=orm['dplace_app.LanguageClass'])),
            ('class2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages2', to=orm['dplace_app.LanguageClass'])),
            ('class3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages3', to=orm['dplace_app.LanguageClass'])),
        ))
        db.send_create_signal(u'dplace_app', ['Language'])

        # Adding model 'LanguageClassification'
        db.create_table(u'dplace_app_languageclassification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=250, db_index=True)),
        ))
        db.send_create_signal(u'dplace_app', ['LanguageClassification'])

        # Adding model 'LanguageClass'
        db.create_table(u'dplace_app_languageclass', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, db_index=True)),
            ('level', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'dplace_app', ['LanguageClass'])

        # Adding model 'LanguageFamily'
        db.create_table(u'dplace_app_languagefamily', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30, db_index=True)),
        ))
        db.send_create_signal(u'dplace_app', ['LanguageFamily'])


    def backwards(self, orm):
        # Deleting model 'Language'
        db.delete_table(u'dplace_app_language')

        # Deleting model 'LanguageClassification'
        db.delete_table(u'dplace_app_languageclassification')

        # Deleting model 'LanguageClass'
        db.delete_table(u'dplace_app_languageclass')

        # Deleting model 'LanguageFamily'
        db.delete_table(u'dplace_app_languagefamily')


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
            'class1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages1'", 'to': u"orm['dplace_app.LanguageClass']"}),
            'class2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages2'", 'to': u"orm['dplace_app.LanguageClass']"}),
            'class3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages3'", 'to': u"orm['dplace_app.LanguageClass']"}),
            'classification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': u"orm['dplace_app.LanguageClassification']"}),
            'family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': u"orm['dplace_app.LanguageFamily']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'to': u"orm['dplace_app.ISOCode']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'dplace_app.languageclass': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'LanguageClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
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