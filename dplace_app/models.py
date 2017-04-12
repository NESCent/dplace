# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict

from django.core.urlresolvers import reverse
from django.db import models


class Society(models.Model):
    ext_id = models.CharField('External ID', db_index=True, unique=True, max_length=20)
    xd_id = models.CharField(
        'Cross ID', db_index=True, default=None, null=True, max_length=10
    )
    name = models.CharField('Name', db_index=True, max_length=200)
    latitude = models.FloatField('Latitude', null=True)
    longitude = models.FloatField('Longitude', null=True)
    focal_year = models.CharField('Focal Year', null=True, blank=True, max_length=100)
    alternate_names = models.TextField(default="")
    original_name = models.CharField('ORIG_name', max_length=200, default=None, null=True)
    original_latitude = models.FloatField('ORIG_latitude', null=True)
    original_longitude = models.FloatField('ORIG_longitude', null=True)
    
    region = models.ForeignKey('GeographicRegion', null=True)
    source = models.ForeignKey('Source', null=True, related_name="societies")
    language = models.ForeignKey('Language', null=True, related_name="societies")
    
    hraf_link = models.CharField('HRAF', null=True, default=None, max_length=200)
    chirila_link = models.CharField('CHIRILA', default=None, null=True, max_length=200)
    relationships = models.ManyToManyField(
        'self', through='SocietyRelation', symmetrical=False)

    @property
    def related(self):
        return list(self.relationships.all())

    @property
    def location(self):
        return dict(coordinates=[self.longitude, self.latitude])
        
    @property
    def original_location(self):
        return dict(coordinates=[self.original_longitude, self.original_latitude])

    def get_environmental_data(self):
        """Returns environmental data for the given society"""
        valueDict = defaultdict(list)
        for value in self.value_set\
                .select_related('variable').order_by('variable__name').all():
            if value.variable.type == 'environmental':
                categories = value.variable.index_categories.all()
                valueDict[str(categories[0])].append({
                    'name': value.variable.name,
                    'value': '{0}'.format(value),
                    'units': value.variable.units,
                    'comment': value.comment
                })
        return valueDict

    def get_cultural_trait_data(self):
        """Returns the data for the given society"""
        valueDict = defaultdict(list)
        for value in self.value_set\
                .select_related('code').\
                select_related('variable').order_by('variable__label').all():
            if value.variable.type == 'cultural':
                categories = value.variable.index_categories.all()
                for c in categories:
                    valueDict[str(c)].append({
                        'id': value.id,
                        'label': value.variable.label,
                        'name': value.variable.name,
                        'code': value.coded_value,
                        'description': value.get_description(),
                        'year': value.focal_year,
                        'comment': value.comment,
                        'sources': value.references.all(),
                    })
        return valueDict

    def get_data_references(self):
        """Returns the references for the cultural trait data"""
        refs = []
        qset = self.value_set
        for value in qset.all():
            for r in value.references.all():
                if r not in refs:
                    refs.append(r)
        return sorted(refs, key=lambda r: r.author)

    def __unicode__(self):
        return "%s - %s" % (self.ext_id, self.name)
    
    def get_absolute_url(self):
        return reverse("view_society", args=[self.ext_id])
    
    class Meta(object):
        verbose_name_plural = "Societies"
        ordering = ('name', )


class SocietyRelation(models.Model):
    from_society = models.ForeignKey(Society, related_name='from_societies')
    to_society = models.ForeignKey(Society, related_name='to_societies')
    type = models.CharField(max_length=100, default='similar')


class Category(models.Model):
    name = models.CharField(max_length=30, db_index=True)
    type = models.CharField(max_length=13)

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("type", "name")


class Variable(models.Model):
    """
    Variables in the Ethnographic Atlas have a number and are accompanied
    by a description, e.g.

        NUMBER: 6, DESCRIPTION: Mode of Marriage (Primary)

    This number is converted to a label: EA006
    """
    label = models.CharField(max_length=50, db_index=True, unique=True)
    name = models.CharField(max_length=200, db_index=True, default='Unknown')
    type = models.CharField(max_length=13)
    source = models.ForeignKey('Source', null=True)
    index_categories = models.ManyToManyField(
        'Category', related_name='index_variables')
    niche_categories = models.ManyToManyField(
        'Category', related_name='niche_variables')
    codebook_info = models.TextField(default='None')
    data_type = models.CharField(max_length=200, null=True)
    units = models.CharField(max_length=100, default='')

    def coded_societies(self):
        return Society.objects.filter(value__in=self.values.all())

    def __unicode__(self):
        res = "%s - %s" % (self.label, self.name)
        if self.units:
            res += " (%s)" % self.units
        return res

    class Meta(object):
        verbose_name = "Variable"
        ordering = ("label", )


class CodeDescription(models.Model):
    """
    Most of the variables in the Ethnographic Atlas are coded with
    discrete values that map to a text description, e.g.

        CODE: 3, DESCRIPTION: 26 - 35% Dependence

    Some coded values to not map to a description, e.g. those that
    represent a 4-digit year

    This model is not used by every value in the EA.

    """
    variable = models.ForeignKey('Variable', db_index=True, related_name="codes")
    code = models.CharField(max_length=20, db_index=True, null=False, default='.')
    code_number = models.IntegerField(null=True, db_index=True)
    description = models.CharField(max_length=500, default='Unknown')
    short_description = models.CharField(max_length=500, default="")
    n = models.IntegerField(null=True, default=0)

    def save(self, *args, **kwargs):
        self.read_code_number()
        super(CodeDescription, self).save(*args, **kwargs)

    def read_code_number(self):
        try:
            self.code_number = int(self.code)
        except ValueError:
            pass

    def coded_societies(self):
        return Society.objects.filter(value__coded_value=self.code)

    def __unicode__(self):
        return "%s - %s" % (self.code, self.description)

    class Meta(object):
        verbose_name = "Code"
        ordering = ("variable", "code_number", "code")


class Value(models.Model):
    """
    The values coded in the EA are typically discrete codes
    that map to a description.  Some are not and
    Most of the variables in the Ethnographic Atlas are coded with
    discrete values that map to a text description, e.g.

        CODE: 3, DESCRIPTION: 26 - 35% Dependence

    Some coded values to not map to a description, e.g. those that
    represent a 4-digit year

    This model is not used by every code

    """
    variable = models.ForeignKey('Variable', related_name="values")
    society = models.ForeignKey('Society')
    coded_value = models.CharField(max_length=100, db_index=True, null=False, default='.')
    coded_value_float = models.FloatField(null=True, db_index=True)
    code = models.ForeignKey('CodeDescription', db_index=True, null=True)
    source = models.ForeignKey('Source', null=True)
    comment = models.TextField(default="")
    references = models.ManyToManyField('Source', related_name="references")
    subcase = models.TextField(default="")
    focal_year = models.CharField(max_length=10, default="")

    def get_description(self):
        return self.code.description if self.code else ''

    def __unicode__(self):
        if self.coded_value_float is not None:
            return "%f" % self.coded_value_float
        return "%s" % self.coded_value

    class Meta(object):
        verbose_name = "Value"
        ordering = ("variable", "coded_value", "coded_value_float")
        index_together = [
            ['variable', 'society', 'focal_year'],
            ['variable', 'coded_value', 'focal_year', 'subcase'],
            ['variable', 'code', 'focal_year'],
            ['society', 'coded_value', 'focal_year', 'subcase'],
            ['society', 'code', 'focal_year'],
        ]
        unique_together = ('variable', 'society', 'coded_value', 'comment', 'subcase', 'focal_year')


class Source(models.Model):
    """
    Stores references for Value, also for dataset sources.
    """
    # Not really sure if we should separate dataset sources from references (I
    # think we should), but since all the code has already been written with
    # this model, I won't change it yet.

    # text, because might be '1996', '1999-2001', or 'ND'
    year = models.CharField(max_length=30, db_index=True)
    author = models.TextField(db_index=True)
    reference = models.TextField()
    name = models.CharField(max_length=100, db_index=True, default="")

    def __unicode__(self):
        return "%s (%s)" % (self.author, self.year)

    class Meta(object):
        unique_together = ('year', 'author')
        ordering = ('name', )
        

class LanguageFamily(models.Model):
    name = models.CharField(max_length=50, db_index=True)

    class Meta(object):
        ordering = ('name', )


class Language(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    glotto_code = models.CharField(max_length=8, null=False, unique=True)

    # needs to be null=True because some glottolog languages do not have isocodes
    iso_code = models.CharField(max_length=3, null=True)
    family = models.ForeignKey('LanguageFamily', null=True)

    def __unicode__(self):
        return "Language: %s, ISO Code %s, Glotto Code %s" % (
            self.name, self.iso_code, self.glotto_code)
    
    def get_absolute_url(self):
        return reverse("view_language", args=[self.glotto_code])
    
    class Meta(object):
        verbose_name = "Language"
        ordering = ('name', )


class GeographicRegion(models.Model):
    level_2_re = models.FloatField()
    count = models.FloatField()
    region_nam = models.CharField(max_length=254, db_index=True)
    continent = models.CharField(max_length=254,  db_index=True)
    tdwg_code = models.IntegerField()

    def __unicode__(self):
        return "Region: %s, Continent %s" % (self.region_nam, self.continent)

    class Meta(object):
        ordering = ('region_nam', )


class LanguageTree(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    newick_string = models.TextField(default='')
    source = models.ForeignKey('Source', null=True)
    taxa = models.ManyToManyField('LanguageTreeLabels')

    class Meta(object):
        ordering = ('name', )


class LanguageTreeLabels(models.Model):
    languageTree = models.ForeignKey('LanguageTree')
    label = models.CharField(max_length=255, db_index=True)
    language = models.ForeignKey('Language', null=True)
    societies = models.ManyToManyField('Society', through="LanguageTreeLabelsSequence")
    
    class Meta:
        ordering = ("-languagetreelabelssequence__fixed_order",)


class LanguageTreeLabelsSequence(models.Model):
    society = models.ForeignKey('Society')
    labels = models.ForeignKey('LanguageTreeLabels')
    fixed_order = models.PositiveSmallIntegerField(db_index=True)
    
    class Meta:
        ordering = ("-fixed_order",)
