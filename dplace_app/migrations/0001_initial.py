# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CulturalCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, db_index=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CulturalCodeDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default='.', max_length=20, db_index=True)),
                ('code_number', models.IntegerField(null=True, db_index=True)),
                ('description', models.CharField(default='Unknown', max_length=500)),
                ('short_description', models.CharField(default='', max_length=500)),
                ('n', models.IntegerField(default=0, null=True)),
            ],
            options={
                'ordering': ('variable', 'code_number', 'code'),
                'verbose_name': 'Code',
            },
        ),
        migrations.CreateModel(
            name='CulturalValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coded_value', models.CharField(default='.', max_length=100, db_index=True)),
                ('comment', models.TextField(default='')),
                ('subcase', models.TextField(default='')),
                ('focal_year', models.CharField(default='', max_length=10)),
                ('code', models.ForeignKey(to='dplace_app.CulturalCodeDescription', null=True)),
            ],
            options={
                'ordering': ('variable', 'coded_value'),
                'verbose_name': 'Value',
            },
        ),
        migrations.CreateModel(
            name='CulturalVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=25, db_index=True)),
                ('name', models.CharField(default='Unknown', max_length=200, db_index=True)),
                ('codebook_info', models.TextField(default='None')),
                ('data_type', models.CharField(max_length=200, null=True)),
                ('index_categories', models.ManyToManyField(related_name='index_variables', to='dplace_app.CulturalCategory')),
                ('niche_categories', models.ManyToManyField(related_name='niche_variables', to='dplace_app.CulturalCategory')),
            ],
            options={
                'ordering': ['label'],
                'verbose_name': 'Variable',
            },
        ),
        migrations.CreateModel(
            name='Environmental',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Environmental',
            },
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
        ),
        migrations.CreateModel(
            name='EnvironmentalValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField(db_index=True)),
                ('environmental', models.ForeignKey(related_name='values', to='dplace_app.Environmental')),
            ],
            options={
                'ordering': ['variable'],
            },
        ),
        migrations.CreateModel(
            name='EnvironmentalVariable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('units', models.CharField(max_length=10, choices=[('mm', 'mm'), ('\u2103', '\u2103'), ('mo', 'mo'), ('', '')])),
                ('codebook_info', models.CharField(default='None', max_length=500)),
                ('category', models.ForeignKey(to='dplace_app.EnvironmentalCategory', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
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
            ],
        ),
        migrations.CreateModel(
            name='ISOCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iso_code', models.CharField(unique=True, max_length=3, verbose_name='ISO Code', db_index=True)),
            ],
            options={
                'verbose_name': 'ISO Code',
            },
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, db_index=True)),
                ('glotto_code', models.CharField(unique=True, max_length=8)),
            ],
            options={
                'verbose_name': 'Language',
            },
        ),
        migrations.CreateModel(
            name='LanguageFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scheme', models.CharField(default='G', max_length=1, choices=[('E', 'Ethnologue17'), ('R', 'Ethnologue17-Revised'), ('G', 'Glottolog')])),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('language_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='LanguageTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, db_index=True)),
                ('file', models.FileField(null=True, upload_to='language_trees')),
                ('newick_string', models.TextField(default='')),
                ('languages', models.ManyToManyField(to='dplace_app.Language')),
            ],
        ),
        migrations.CreateModel(
            name='Society',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ext_id', models.CharField(unique=True, max_length=10, verbose_name='External ID')),
                ('xd_id', models.CharField(default=None, max_length=10, null=True, verbose_name='Cross ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name', db_index=True)),
                ('latitude', models.FloatField(null=True, verbose_name='Latitude')),
                ('longitude', models.FloatField(null=True, verbose_name='Longitude')),
                ('focal_year', models.CharField(max_length=100, null=True, verbose_name='Focal Year', blank=True)),
                ('alternate_names', models.TextField(default='')),
                ('language', models.ForeignKey(related_name='societies', to='dplace_app.Language', null=True)),
                ('region', models.ForeignKey(related_name='societies', to='dplace_app.GeographicRegion', null=True)),
            ],
            options={
                'verbose_name_plural': 'Societies',
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=30)),
                ('author', models.CharField(max_length=50)),
                ('reference', models.CharField(max_length=500)),
                ('name', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='source',
            unique_together=set([('year', 'author')]),
        ),
        migrations.AddField(
            model_name='society',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='languagetree',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='family',
            field=models.ForeignKey(to='dplace_app.LanguageFamily', null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='iso_code',
            field=models.ForeignKey(to='dplace_app.ISOCode', null=True),
        ),
        migrations.AddField(
            model_name='environmentalvalue',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='environmentalvalue',
            name='variable',
            field=models.ForeignKey(related_name='values', to='dplace_app.EnvironmentalVariable'),
        ),
        migrations.AddField(
            model_name='environmental',
            name='iso_code',
            field=models.ForeignKey(related_name='environmentals', to='dplace_app.ISOCode', null=True),
        ),
        migrations.AddField(
            model_name='environmental',
            name='society',
            field=models.ForeignKey(related_name='environmentals', to='dplace_app.Society', null=True),
        ),
        migrations.AddField(
            model_name='environmental',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='culturalvariable',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='culturalvalue',
            name='references',
            field=models.ManyToManyField(related_name='references', to='dplace_app.Source'),
        ),
        migrations.AddField(
            model_name='culturalvalue',
            name='society',
            field=models.ForeignKey(to='dplace_app.Society', null=True),
        ),
        migrations.AddField(
            model_name='culturalvalue',
            name='source',
            field=models.ForeignKey(to='dplace_app.Source', null=True),
        ),
        migrations.AddField(
            model_name='culturalvalue',
            name='variable',
            field=models.ForeignKey(related_name='values', to='dplace_app.CulturalVariable'),
        ),
        migrations.AddField(
            model_name='culturalcodedescription',
            name='variable',
            field=models.ForeignKey(related_name='codes', to='dplace_app.CulturalVariable'),
        ),
        migrations.AlterUniqueTogether(
            name='language',
            unique_together=set([('iso_code', 'glotto_code')]),
        ),
        migrations.AlterUniqueTogether(
            name='environmentalvalue',
            unique_together=set([('variable', 'environmental')]),
        ),
        migrations.AlterIndexTogether(
            name='environmentalvalue',
            index_together=set([('variable', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='culturalvalue',
            unique_together=set([('variable', 'society', 'coded_value')]),
        ),
        migrations.AlterIndexTogether(
            name='culturalvalue',
            index_together=set([('variable', 'society'), ('variable', 'code'), ('society', 'code'), ('society', 'coded_value'), ('variable', 'coded_value')]),
        ),
    ]
