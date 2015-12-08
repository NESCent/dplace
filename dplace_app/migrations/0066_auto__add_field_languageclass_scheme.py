# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'LanguageClass.scheme'
        db.add_column(u'dplace_app_languageclass', 'scheme',
                      self.gf('django.db.models.fields.CharField')(default='G', max_length=1),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'LanguageClass.scheme'
        db.delete_column(u'dplace_app_languageclass', 'scheme')


    models = {
        u'dplace_app.environmental': {
            'Meta': {'object_name': 'Environmental'},
            'actual_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'reported_location': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environmentals'", 'null': 'True', 'to': u"orm['dplace_app.Society']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'})
        },
        u'dplace_app.environmentalcategory': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EnvironmentalCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30', 'db_index': 'True'})
        },
        u'dplace_app.environmentalvalue': {
            'Meta': {'ordering': "('variable',)", 'unique_together': "(('variable', 'environmental'),)", 'object_name': 'EnvironmentalValue', 'index_together': "[['variable', 'value']]"},
            'environmental': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.Environmental']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.EnvironmentalVariable']"})
        },
        u'dplace_app.environmentalvariable': {
            'Meta': {'ordering': "('name',)", 'object_name': 'EnvironmentalVariable'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.EnvironmentalCategory']", 'null': 'True'}),
            'codebook_info': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'units': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'dplace_app.geographicregion': {
            'Meta': {'object_name': 'GeographicRegion'},
            'continent': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'count': ('django.db.models.fields.FloatField', [], {}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level_2_re': ('django.db.models.fields.FloatField', [], {}),
            'region_nam': ('django.db.models.fields.CharField', [], {'max_length': '254'}),
            'tdwg_code': ('django.db.models.fields.IntegerField', [], {})
        },
        u'dplace_app.glottocode': {
            'Meta': {'object_name': 'GlottoCode'},
            'glotto_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'dplace_app.isocode': {
            'Meta': {'object_name': 'ISOCode'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'})
        },
        u'dplace_app.language': {
            'Meta': {'object_name': 'Language'},
            'glotto_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.GlottoCode']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.ISOCode']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'dplace_app.languageclass': {
            'Meta': {'ordering': "('level', 'name')", 'object_name': 'LanguageClass'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['dplace_app.LanguageClass']", 'null': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'})
        },
        u'dplace_app.languageclassification': {
            'Meta': {'ordering': "('language__name',)", 'object_name': 'LanguageClassification', 'index_together': "[['class_family', 'class_subfamily', 'class_subsubfamily'], ['scheme', 'class_family']]"},
            'class_family': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages1'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class_subfamily': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages2'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            'class_subsubfamily': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'languages3'", 'null': 'True', 'to': u"orm['dplace_app.LanguageClass']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Language']", 'null': 'True'}),
            'scheme': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'})
        },
        u'dplace_app.languagetree': {
            'Meta': {'object_name': 'LanguageTree'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'languages': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['dplace_app.Language']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'newick_string': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'})
        },
        u'dplace_app.society': {
            'Meta': {'object_name': 'Society'},
            'alternate_names': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'ext_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'focal_year': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'glotto_code': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.GlottoCode']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.ISOCode']"}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'societies'", 'null': 'True', 'to': u"orm['dplace_app.Language']"}),
            'location': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'}),
            'xd_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '10', 'null': 'True'})
        },
        u'dplace_app.source': {
            'Meta': {'unique_together': "(('year', 'author'),)", 'object_name': 'Source'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'subcase': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'year': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'dplace_app.variablecategory': {
            'Meta': {'ordering': "('name',)", 'object_name': 'VariableCategory'},
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
            'short_description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'codes'", 'to': u"orm['dplace_app.VariableDescription']"})
        },
        u'dplace_app.variablecodedvalue': {
            'Meta': {'ordering': "('variable', 'coded_value')", 'unique_together': "(('variable', 'society', 'coded_value'),)", 'object_name': 'VariableCodedValue', 'index_together': "[['variable', 'society'], ['variable', 'coded_value'], ['variable', 'code'], ['society', 'coded_value'], ['society', 'code']]"},
            'code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.VariableCodeDescription']", 'null': 'True'}),
            'coded_value': ('django.db.models.fields.CharField', [], {'default': "'.'", 'max_length': '100', 'db_index': 'True'}),
            'focal_year': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'society': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Society']", 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'}),
            'variable': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': u"orm['dplace_app.VariableDescription']"})
        },
        u'dplace_app.variabledescription': {
            'Meta': {'ordering': "('label',)", 'object_name': 'VariableDescription'},
            'codebook_info': ('django.db.models.fields.TextField', [], {'default': "'None'"}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'index_variables'", 'symmetrical': 'False', 'to': u"orm['dplace_app.VariableCategory']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '25', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '200', 'db_index': 'True'}),
            'niche_categories': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'niche_variables'", 'symmetrical': 'False', 'to': u"orm['dplace_app.VariableCategory']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.Source']", 'null': 'True'})
        }
    }

    complete_apps = ['dplace_app']