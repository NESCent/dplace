# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ISOCode'
        db.create_table(u'dplace_app_isocode', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=16, db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal(u'dplace_app', ['ISOCode'])

        # Adding model 'Society'
        db.create_table(u'dplace_app_society', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ext_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('iso_code', self.gf('django.db.models.fields.related.ForeignKey')(related_name='societies', null=True, to=orm['dplace_app.ISOCode'])),
        ))
        db.send_create_signal(u'dplace_app', ['Society'])

        # Adding model 'Environmental'
        db.create_table(u'dplace_app_environmental', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('society', self.gf('django.db.models.fields.related.ForeignKey')(related_name='environmentals', null=True, to=orm['dplace_app.Society'])),
            ('reported_location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('actual_location', self.gf('django.contrib.gis.db.models.fields.PointField')()),
            ('iso_code', self.gf('django.db.models.fields.related.ForeignKey')(related_name='environmentals', null=True, to=orm['dplace_app.ISOCode'])),
            ('annual_mean_temperature', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('annual_temperature_variance', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('temperature_constancy', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('temperature_contingency', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('temperature_predictability', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('annual_mean_precipitation', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('annual_precipitation_variance', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('precipitation_constancy', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('precipitation_contingency', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('precipitation_predictability', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('mean_growing_season_duration', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('net_primary_productivity', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('bird_diversity', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('mammal_diversity', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('amphibian_diversity', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('plant_diversity', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('elevation', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('slope', self.gf('django.db.models.fields.FloatField')(null=True)),
        ))
        db.send_create_signal(u'dplace_app', ['Environmental'])

        # Adding model 'EAVariableDescription'
        db.create_table(u'dplace_app_eavariabledescription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableDescription'])

        # Adding model 'EAVariableCodeDescription'
        db.create_table(u'dplace_app_eavariablecodedescription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variable', self.gf('django.db.models.fields.related.ForeignKey')(related_name='codes', to=orm['dplace_app.EAVariableDescription'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableCodeDescription'])

        # Adding model 'EAVariableValue'
        db.create_table(u'dplace_app_eavariablevalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.EAVariableCodeDescription'])),
            ('society', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.Society'])),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableValue'])


    def backwards(self, orm):
        # Deleting model 'ISOCode'
        db.delete_table(u'dplace_app_isocode')

        # Deleting model 'Society'
        db.delete_table(u'dplace_app_society')

        # Deleting model 'Environmental'
        db.delete_table(u'dplace_app_environmental')

        # Deleting model 'EAVariableDescription'
        db.delete_table(u'dplace_app_eavariabledescription')

        # Deleting model 'EAVariableCodeDescription'
        db.delete_table(u'dplace_app_eavariablecodedescription')

        # Deleting model 'EAVariableValue'
        db.delete_table(u'dplace_app_eavariablevalue')


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
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '16', 'db_index': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {})
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