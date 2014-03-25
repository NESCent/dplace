# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnvironmentalValue'
        db.create_table(u'dplace_app_environmentalvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variable', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.EnvironmentalVariable'])),
            ('value', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('environmental', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['dplace_app.Environmental'])),
        ))
        db.send_create_signal(u'dplace_app', ['EnvironmentalValue'])

        # Adding unique constraint on 'EnvironmentalValue', fields ['variable', 'environmental']
        db.create_unique(u'dplace_app_environmentalvalue', ['variable_id', 'environmental_id'])

        # Adding index on 'EnvironmentalValue', fields ['variable', 'value']
        db.create_index(u'dplace_app_environmentalvalue', ['variable_id', 'value'])

        # Adding model 'EnvironmentalVariable'
        db.create_table(u'dplace_app_environmentalvariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('units', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'dplace_app', ['EnvironmentalVariable'])

        # Deleting field 'Environmental.slope'
        db.delete_column(u'dplace_app_environmental', 'slope')

        # Deleting field 'Environmental.precipitation_contingency'
        db.delete_column(u'dplace_app_environmental', 'precipitation_contingency')

        # Deleting field 'Environmental.annual_mean_temperature'
        db.delete_column(u'dplace_app_environmental', 'annual_mean_temperature')

        # Deleting field 'Environmental.bird_diversity'
        db.delete_column(u'dplace_app_environmental', 'bird_diversity')

        # Deleting field 'Environmental.mammal_diversity'
        db.delete_column(u'dplace_app_environmental', 'mammal_diversity')

        # Deleting field 'Environmental.precipitation_constancy'
        db.delete_column(u'dplace_app_environmental', 'precipitation_constancy')

        # Deleting field 'Environmental.net_primary_productivity'
        db.delete_column(u'dplace_app_environmental', 'net_primary_productivity')

        # Deleting field 'Environmental.mean_growing_season_duration'
        db.delete_column(u'dplace_app_environmental', 'mean_growing_season_duration')

        # Deleting field 'Environmental.temperature_predictability'
        db.delete_column(u'dplace_app_environmental', 'temperature_predictability')

        # Deleting field 'Environmental.plant_diversity'
        db.delete_column(u'dplace_app_environmental', 'plant_diversity')

        # Deleting field 'Environmental.precipitation_predictability'
        db.delete_column(u'dplace_app_environmental', 'precipitation_predictability')

        # Deleting field 'Environmental.elevation'
        db.delete_column(u'dplace_app_environmental', 'elevation')

        # Deleting field 'Environmental.amphibian_diversity'
        db.delete_column(u'dplace_app_environmental', 'amphibian_diversity')

        # Deleting field 'Environmental.temperature_contingency'
        db.delete_column(u'dplace_app_environmental', 'temperature_contingency')

        # Deleting field 'Environmental.annual_mean_precipitation'
        db.delete_column(u'dplace_app_environmental', 'annual_mean_precipitation')

        # Deleting field 'Environmental.annual_precipitation_variance'
        db.delete_column(u'dplace_app_environmental', 'annual_precipitation_variance')

        # Deleting field 'Environmental.annual_temperature_variance'
        db.delete_column(u'dplace_app_environmental', 'annual_temperature_variance')

        # Deleting field 'Environmental.temperature_constancy'
        db.delete_column(u'dplace_app_environmental', 'temperature_constancy')


    def backwards(self, orm):
        # Removing index on 'EnvironmentalValue', fields ['variable', 'value']
        db.delete_index(u'dplace_app_environmentalvalue', ['variable_id', 'value'])

        # Removing unique constraint on 'EnvironmentalValue', fields ['variable', 'environmental']
        db.delete_unique(u'dplace_app_environmentalvalue', ['variable_id', 'environmental_id'])

        # Deleting model 'EnvironmentalValue'
        db.delete_table(u'dplace_app_environmentalvalue')

        # Deleting model 'EnvironmentalVariable'
        db.delete_table(u'dplace_app_environmentalvariable')

        # Adding field 'Environmental.slope'
        db.add_column(u'dplace_app_environmental', 'slope',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.precipitation_contingency'
        db.add_column(u'dplace_app_environmental', 'precipitation_contingency',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.annual_mean_temperature'
        db.add_column(u'dplace_app_environmental', 'annual_mean_temperature',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.bird_diversity'
        db.add_column(u'dplace_app_environmental', 'bird_diversity',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.mammal_diversity'
        db.add_column(u'dplace_app_environmental', 'mammal_diversity',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.precipitation_constancy'
        db.add_column(u'dplace_app_environmental', 'precipitation_constancy',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.net_primary_productivity'
        db.add_column(u'dplace_app_environmental', 'net_primary_productivity',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.mean_growing_season_duration'
        db.add_column(u'dplace_app_environmental', 'mean_growing_season_duration',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.temperature_predictability'
        db.add_column(u'dplace_app_environmental', 'temperature_predictability',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.plant_diversity'
        db.add_column(u'dplace_app_environmental', 'plant_diversity',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.precipitation_predictability'
        db.add_column(u'dplace_app_environmental', 'precipitation_predictability',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.elevation'
        db.add_column(u'dplace_app_environmental', 'elevation',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.amphibian_diversity'
        db.add_column(u'dplace_app_environmental', 'amphibian_diversity',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.temperature_contingency'
        db.add_column(u'dplace_app_environmental', 'temperature_contingency',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.annual_mean_precipitation'
        db.add_column(u'dplace_app_environmental', 'annual_mean_precipitation',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.annual_precipitation_variance'
        db.add_column(u'dplace_app_environmental', 'annual_precipitation_variance',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.annual_temperature_variance'
        db.add_column(u'dplace_app_environmental', 'annual_temperature_variance',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'Environmental.temperature_constancy'
        db.add_column(u'dplace_app_environmental', 'temperature_constancy',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)


    models = {
        u'dplace_app.environmental': {
            'Meta': {'object_name': 'Environmental'},
            'actual_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'reported_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.Society']"})
        },
        u'dplace_app.environmentalvalue': {
            'Meta': {'unique_together': "(('variable', 'environmental'),)", 'object_name': 'EnvironmentalValue', 'index_together': "[['variable', 'value']]"},
            'environmental': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.Environmental']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.EnvironmentalVariable']"})
        },
        u'dplace_app.environmentalvariable': {
            'Meta': {'object_name': 'EnvironmentalVariable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'dplace_app.isocode': {
            'Meta': {'object_name': 'ISOCode'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'})
        },
        u'dplace_app.language': {
            'Meta': {'object_name': 'Language'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages'", 'unique': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
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
            'ethnologue_classification': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Language']", 'null': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'E'", 'max_length': '1'})
        },
        u'dplace_app.society': {
            'Meta': {'object_name': 'Society'},
            'ext_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.Language']"}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'dplace_app.source': {
            'Meta': {'unique_together': "(('year', 'author'),)", 'object_name': 'Source'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'focal_year': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'subcase': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'dplace_app.variablecategory': {
            'Meta': {'object_name': 'VariableCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'})
        },
        u'dplace_app.variablecodedescription': {
            'Meta': {'ordering': "('variable', 'code_number', 'code')", 'object_name': 'VariableCodeDescription'},
            'code': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '20', 'db_index': 'True'}),
            'code_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_index': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'n': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'codes'", 'to': u"orm['dplace_app.VariableDescription']"})
        },
        u'dplace_app.variablecodedvalue': {
            'Meta': {'ordering': "('variable', 'coded_value')", 'unique_together': "(('variable', 'society', 'coded_value'),)", 'object_name': 'VariableCodedValue', 'index_together': "[['variable', 'society'], ['variable', 'coded_value'], ['variable', 'code'], ['society', 'coded_value'], ['society', 'code']]"},
            'code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.VariableCodeDescription']", 'null': 'True'}),
            'coded_value': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '20', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Society']", 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.VariableDescription']"})
        },
        u'dplace_app.variabledescription': {
            'Meta': {'ordering': "('label',)", 'object_name': 'VariableDescription'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'index_variables'", 'symmetrical': 'False', 'to': u"orm['dplace_app.VariableCategory']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '200', 'db_index': 'True'}),
            'niche_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'niche_variables'", 'symmetrical': 'False', 'to': u"orm['dplace_app.VariableCategory']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'})
        }
    }

    complete_apps = ['dplace_app']