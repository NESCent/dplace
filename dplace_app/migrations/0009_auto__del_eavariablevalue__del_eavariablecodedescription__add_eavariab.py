# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'EAVariableValue'
        db.delete_table(u'dplace_app_eavariablevalue')

        # Deleting model 'EAVariableCodeDescription'
        db.delete_table(u'dplace_app_eavariablecodedescription')

        # Adding model 'EAVariableCodedValue'
        db.create_table(u'dplace_app_eavariablecodedvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variable', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.EAVariableDescription'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableCodedValue'])

        # Adding M2M table for field societies on 'EAVariableCodedValue'
        m2m_table_name = db.shorten_name(u'dplace_app_eavariablecodedvalue_societies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('eavariablecodedvalue', models.ForeignKey(orm[u'dplace_app.eavariablecodedvalue'], null=False)),
            ('society', models.ForeignKey(orm[u'dplace_app.society'], null=False))
        ))
        db.create_unique(m2m_table_name, ['eavariablecodedvalue_id', 'society_id'])


    def backwards(self, orm):
        # Adding model 'EAVariableValue'
        db.create_table(u'dplace_app_eavariablevalue', (
            ('code', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.EAVariableCodeDescription'])),
            ('society', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.Society'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableValue'])

        # Adding model 'EAVariableCodeDescription'
        db.create_table(u'dplace_app_eavariablecodedescription', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('variable', self.gf('django.db.models.fields.related.ForeignKey')(related_name='codes', to=orm['dplace_app.EAVariableDescription'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dplace_app', ['EAVariableCodeDescription'])

        # Deleting model 'EAVariableCodedValue'
        db.delete_table(u'dplace_app_eavariablecodedvalue')

        # Removing M2M table for field societies on 'EAVariableCodedValue'
        db.delete_table(db.shorten_name(u'dplace_app_eavariablecodedvalue_societies'))


    models = {
        u'dplace_app.eavariablecodedvalue': {
            'Meta': {'ordering': "('variable', 'code')", 'object_name': 'EAVariableCodedValue'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'societies': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dplace_app.Society']", 'symmetrical': 'False'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.EAVariableDescription']"})
        },
        u'dplace_app.eavariabledescription': {
            'Meta': {'ordering': "('number',)", 'object_name': 'EAVariableDescription'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
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