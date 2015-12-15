# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Environmental',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reported_location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('actual_location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                'verbose_name': 'Environmental',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentalCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentalValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(db_index=True)),
                ('environmental', models.ForeignKey(related_name='values', to='dplace_app.Environmental')),
            ],
            options={
                'ordering': ('variable',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentalVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('units', models.CharField(max_length=10, choices=[(b'mm', b'mm'), (b'\xe2\x84\x83', b'\xe2\x84\x83'), (b'mo', b'mo'), (b'', b'')])),
                ('codebook_info', models.CharField(default=b'None', max_length=500)),
                ('category', models.ForeignKey(to='dplace_app.EnvironmentalCategory', null=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicRegion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('level_2_re', models.FloatField()),
                ('count', models.FloatField()),
                ('region_nam', models.CharField(max_length=254)),
                ('continent', models.CharField(max_length=254)),
                ('tdwg_code', models.IntegerField()),
                ('geom', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GlottoCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('glotto_code', models.CharField(max_length=10, verbose_name=b'Glotto Code', db_index=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ISOCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_code', models.CharField(max_length=3, verbose_name=b'ISO Code', db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True)),
            ],
            options={
                'verbose_name': 'ISO Code',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('glotto_code', models.ForeignKey(null=True, to='dplace_app.GlottoCode', unique=True)),
                ('iso_code', models.ForeignKey(to='dplace_app.ISOCode', null=True)),
            ],
            options={
                'verbose_name': 'Language',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scheme', models.CharField(default=b'G', max_length=1, choices=[(b'E', b'Ethnologue17'), (b'R', b'Ethnologue17-Revised'), (b'G', b'Glottolog')])),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('level', models.IntegerField(db_index=True, choices=[(1, b'Family'), (2, b'Subfamily'), (3, b'Subsubfamily')])),
                ('language_count', models.IntegerField(default=0)),
                ('parent', models.ForeignKey(default=None, to='dplace_app.LanguageClass', null=True)),
            ],
            options={
                'ordering': ('level', 'name'),
                'verbose_name': 'Language Class',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scheme', models.CharField(default=b'G', max_length=1, choices=[(b'E', b'Ethnologue17'), (b'R', b'Ethnologue17-Revised'), (b'G', b'Glottolog')])),
                ('class_family', models.ForeignKey(related_name='languages1', to='dplace_app.LanguageClass', null=True)),
                ('class_subfamily', models.ForeignKey(related_name='languages2', to='dplace_app.LanguageClass', null=True)),
                ('class_subsubfamily', models.ForeignKey(related_name='languages3', to='dplace_app.LanguageClass', null=True)),
                ('language', models.ForeignKey(to='dplace_app.Language', null=True)),
            ],
            options={
                'ordering': ('language__name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('file', models.FileField(null=True, upload_to=b'language_trees')),
                ('newick_string', models.TextField(default=b'')),
                ('languages', models.ManyToManyField(to='dplace_app.Language')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ext_id', models.CharField(unique=True, max_length=10, verbose_name=b'External ID')),
                ('xd_id', models.CharField(default=None, max_length=10, null=True, verbose_name=b'Cross ID')),
                ('name', models.CharField(max_length=200, verbose_name=b'Name', db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name=b'Location')),
                ('focal_year', models.CharField(max_length=100, null=True, verbose_name=b'Focal Year', blank=True)),
                ('alternate_names', models.TextField(default=b'')),
                ('language', models.ForeignKey(related_name='societies', to='dplace_app.Language', null=True)),
            ],
            options={
                'verbose_name_plural': 'Societies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=30)),
                ('author', models.CharField(max_length=50)),
                ('reference', models.CharField(max_length=500)),
                ('name', models.CharField(default=b'', max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariableCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, db_index=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariableCodeDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=b'.', max_length=20, db_index=True)),
                ('code_number', models.IntegerField(null=True, db_index=True)),
                ('description', models.CharField(default=b'Unknown', max_length=500)),
                ('short_description', models.CharField(default=b'', max_length=500)),
                ('n', models.IntegerField(default=0, null=True)),
            ],
            options={
                'ordering': ('variable', 'code_number', 'code'),
                'verbose_name': 'Code',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariableCodedValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coded_value', models.CharField(default=b'.', max_length=100, db_index=True)),
                ('comment', models.TextField(default=b'')),
                ('subcase', models.TextField(default=b'')),
                ('focal_year', models.CharField(default=b'', max_length=10)),
                ('code', models.ForeignKey(to='dplace_app.VariableCodeDescription', null=True)),
                ('references', models.ManyToManyField(related_name='references', to='dplace_app.Source')),
                ('society', models.ForeignKey(to='dplace_app.Society', null=True)),
                ('source', models.ForeignKey(to='dplace_app.Source', null=True)),
            ],
            options={
                'ordering': ('variable', 'coded_value'),
                'verbose_name': 'Value',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VariableDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=25, db_index=True)),
                ('name', models.CharField(default=b'Unknown', max_length=200, db_index=True)),
                ('codebook_info', models.TextField(default=b'None')),
                ('data_type', models.CharField(max_length=200, null=True)),
                ('index_categories', models.ManyToManyField(related_name='index_variables', to='dplace_app.VariableCategory')),
                ('niche_categories', models.ManyToManyField(related_name='niche_variables', to='dplace_app.VariableCategory')),
                ('source', models.ForeignKey(to='dplace_app.Source', null=True)),
            ],
            options={
                'ordering': ('label',),
                'verbose_name': 'Variable',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='variablecodedvalue',
            name='variable',
            field=models.ForeignKey(related_name='values', to='dplace_app.VariableDescription'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='variablecodedvalue',
            unique_together=set([('variable', 'society', 'coded_value')]),
        ),
        migrations.AlterIndexTogether(
            name='variablecodedvalue',
            index_together=set([('variable', 'society'), ('variable', 'code'), ('society', 'code'), ('society', 'coded_value'), ('variable', 'coded_value')]),
        ),
        migrations.AddField(
            model_name='variablecodedescription',
            name='variable',
            field=models.ForeignKey(related_name='codes', to='dplace_app.VariableDescription'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='source',
            unique_together=set([('year', 'author')]),
        ),
        migrations.AddField(
            model_name='society',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='languagetree',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
            preserve_default=True,
        ),
        migrations.AlterIndexTogether(
            name='languageclassification',
            index_together=set([('class_family', 'class_subfamily', 'class_subsubfamily'), ('scheme', 'class_family')]),
        ),
        migrations.AlterUniqueTogether(
            name='language',
            unique_together=set([('iso_code', 'glotto_code')]),
        ),
        migrations.AddField(
            model_name='environmentalvalue',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environmentalvalue',
            name='variable',
            field=models.ForeignKey(related_name='values', to='dplace_app.EnvironmentalVariable'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='environmentalvalue',
            unique_together=set([('variable', 'environmental')]),
        ),
        migrations.AlterIndexTogether(
            name='environmentalvalue',
            index_together=set([('variable', 'value')]),
        ),
        migrations.AddField(
            model_name='environmental',
            name='iso_code',
            field=models.ForeignKey(related_name='environmentals', to='dplace_app.ISOCode', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environmental',
            name='society',
            field=models.ForeignKey(related_name='environmentals', to='dplace_app.Society', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environmental',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
            preserve_default=True,
        ),
    ]
