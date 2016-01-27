# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'LanguageClass'
        db.delete_table(u'dplace_app_languageclass')

        # Deleting model 'LanguageClassification'
        db.delete_table(u'dplace_app_languageclassification')

        # Removing index on 'LanguageClassification', fields ['class_family', 'class_subfamily', 'class_subsubfamily']
        #db.delete_index(u'dplace_app_languageclassification', ['class_family_id', 'class_subfamily_id', 'class_subsubfamily_id'])

        # Removing index on 'LanguageClassification', fields ['scheme', 'class_family']
        #db.delete_index(u'dplace_app_languageclassification', ['scheme', 'class_family_id'])


    def backwards(self, orm):
        # Adding index on 'LanguageClassification', fields ['scheme', 'class_family']
        db.create_index(u'dplace_app_languageclassification', ['scheme', 'class_family_id'])

        # Adding index on 'LanguageClassification', fields ['class_family', 'class_subfamily', 'class_subsubfamily']
        db.create_index(u'dplace_app_languageclassification', ['class_family_id', 'class_subfamily_id', 'class_subsubfamily_id'])

        # Adding model 'LanguageClass'
        db.create_table(u'dplace_app_languageclass', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['dplace_app.LanguageClass'], null=True)),
            ('level', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('scheme', self.gf('django.db.models.fields.CharField')(default='G', max_length=1)),
            ('language_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'dplace_app', ['LanguageClass'])

        # Adding model 'LanguageClassification'
        db.create_table(u'dplace_app_languageclassification', (
            ('class_subsubfamily', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages3', null=True, to=orm['dplace_app.LanguageClass'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dplace_app.Language'], null=True)),
            ('class_subfamily', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages2', null=True, to=orm['dplace_app.LanguageClass'])),
            ('scheme', self.gf('django.db.models.fields.CharField')(default='G', max_length=1)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('class_family', self.gf('django.db.models.fields.related.ForeignKey')(related_name='languages1', null=True, to=orm['dplace_app.LanguageClass'])),
        ))
        db.send_create_signal(u'dplace_app', ['LanguageClassification'])


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
            'Meta': {'unique_together': "(('iso_code', 'glotto_code'),)", 'object_name': 'Language'},
            'family': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.LanguageFamily']", 'null': 'True'}),
            'glotto_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.GlottoCode']", 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dplace_app.ISOCode']", 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'dplace_app.languagefamily': {
            'Meta': {'object_name': 'LanguageFamily'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'subcase': ('django.db.models.fields.TextField', [], {'default': "''"}),
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