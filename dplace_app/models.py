# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict

from django.contrib.gis.db import models

UNIT_CHOICES = (
    ('mm', 'mm'),
    ('℃', '℃'),
    ('mo', 'mo'),
    ('', ''),
)

CLASS_LEVELS = (
    (1, 'Family'),
    (2, 'Subfamily'),
    (3, 'Subsubfamily')
)


CLASSIFICATION_SCHEMES = (
    ('E', 'Ethnologue17',),
    ('R', 'Ethnologue17-Revised',),
    ('G', 'Glottolog',),
)


# Originally from 'iso lat long.xlsx'.  This spreadsheet contains ISO Codes and
# their Locations.  Only iso codes from the 16th edition ethnologue were
# present.  Other datasets references ISO Codes that were not present in 16th
# ed, so now this is loaded from the ethnologue, and locations are annotated
# later if known

# We don't really need a location field here...
class ISOCode(models.Model):
    iso_code = models.CharField('ISO Code', db_index=True, max_length=3)
    # only have locations for ISO codes in 16th ed ethnologue
    objects = models.GeoManager()   # For GeoDjango, must override the manager

    def __unicode__(self):
        return "%s" % (self.iso_code)

    class Meta(object):
        verbose_name = "ISO Code"


class GlottoCode(models.Model):
    glotto_code = models.CharField('Glotto Code', db_index=True, max_length=10)

    def __unicode__(self):
        return "%s" % self.glotto_code


class Society(models.Model):
    ext_id = models.CharField('External ID', unique=True, max_length=10)
    xd_id = models.CharField(
        'Cross ID', default=None, null=True, max_length=10)
    name = models.CharField('Name', db_index=True, max_length=200)
    location = models.PointField('Location', null=True)
    source = models.ForeignKey('Source', null=True)
    language = models.ForeignKey(
        'Language', null=True, related_name="societies")
    objects = models.GeoManager()
    focal_year = models.CharField(
        'Focal Year', null=True, blank=True, max_length=100)
    alternate_names = models.TextField(default="")

    def get_environmental_data(self):
        """Returns environmental data for the given society"""
        valueDict = defaultdict(list)
        environmentals = self.environmentals.all()
        for environmental in environmentals:
            for value in environmental.values.order_by('variable__name').all():
                valueDict[str(value.variable.category)].append({
                    'name': value.variable.name,
                    'value': format(value.value, '.4f'),
                    'units': value.variable.units
                })
        return valueDict

    def get_cultural_trait_data(self):
        """Returns the data for the given society"""
        valueDict = defaultdict(list)
        qset = self.variablecodedvalue_set.select_related('code')
        qset = qset.select_related('variable')
        for value in qset.order_by('variable__label').all():
            categories = value.variable.index_categories.all()
            for c in categories:
                valueDict[str(c)].append({
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
        qset = self.variablecodedvalue_set
        for value in qset.all():
            for r in value.references.all():
                if r not in refs:
                    refs.append(r)
        return sorted(refs, key=lambda r: r.author)

    def __unicode__(self):
        return "%s - %s (%s)" % (self.ext_id, self.name, self.source)

    class Meta(object):
        verbose_name_plural = "Societies"


class EnvironmentalCategory(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("name",)


class EnvironmentalVariable(models.Model):
    name = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey('EnvironmentalCategory', null=True)
    units = models.CharField(max_length=10, choices=UNIT_CHOICES)
    codebook_info = models.CharField(max_length=500, default='None')

    def __unicode__(self):
        if self.units:
            return "%s (%s)" % (self.name, self.units)
        return self.name

    class Meta(object):
        ordering = ["name"]


class EnvironmentalValue(models.Model):
    variable = models.ForeignKey('EnvironmentalVariable', related_name="values")
    value = models.FloatField(db_index=True)
    environmental = models.ForeignKey('Environmental', related_name="values")
    source = models.ForeignKey('Source', null=True)

    def society(self):
        return self.environmental.society

    def __unicode__(self):
        return "%f" % self.value

    class Meta(object):
        ordering = ["variable"]
        unique_together = ('variable', 'environmental')
        index_together = ['variable', 'value']


class Environmental(models.Model):
    society = models.ForeignKey('Society', null=True, related_name="environmentals")
    iso_code = models.ForeignKey('ISOCode', null=True, related_name="environmentals")
    source = models.ForeignKey('Source', null=True)
    objects = models.GeoManager()   # For GeoDjango, must override the manager

    def __unicode__(self):
        return "%d Society: %d" % (self.id, self.society_id)

    class Meta(object):
        verbose_name = "Environmental"


class VariableDescription(models.Model):
    """
    Variables in the Ethnographic Atlas have a number and are accompanied
    by a description, e.g.

        NUMBER: 6, DESCRIPTION: Mode of Marriage (Primary)

    This number is converted to a label: EA006
    """
    label = models.CharField(max_length=25, db_index=True)
    name = models.CharField(max_length=200, db_index=True, default='Unknown')
    source = models.ForeignKey('Source', null=True)
    index_categories = models.ManyToManyField(
        'VariableCategory', related_name='index_variables')
    niche_categories = models.ManyToManyField(
        'VariableCategory', related_name='niche_variables')
    codebook_info = models.TextField(default='None')
    data_type = models.CharField(max_length=200, null=True)

    def coded_societies(self):
        return Society.objects.filter(variablecodedvalue__in=self.values.all())

    def __unicode__(self):
        return "%s - %s" % (self.label, self.name)

    class Meta(object):
        verbose_name = "Variable"
        ordering = ["label"]


class VariableCategory(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)

    def __unicode__(self):
        return self.name

    class Meta(object):
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]


class VariableCodeDescription(models.Model):
    """
    Most of the variables in the Ethnographic Atlas are coded with
    discrete values that map to a text description, e.g.

        CODE: 3, DESCRIPTION: 26 - 35% Dependence

    Some coded values to not map to a description, e.g. those that
    represent a 4-digit year

    This model is not used by every value in the EA.

    """
    variable = models.ForeignKey(
        'VariableDescription', related_name="codes", db_index=True)
    code = models.CharField(
        max_length=20, db_index=True, null=False, default='.')
    code_number = models.IntegerField(null=True, db_index=True)
    description = models.CharField(max_length=500, default='Unknown')
    short_description = models.CharField(max_length=500, default="")
    n = models.IntegerField(null=True, default=0)

    def save(self, *args, **kwargs):
        self.read_code_number()
        super(VariableCodeDescription, self).save(*args, **kwargs)

    def read_code_number(self):
        try:
            self.code_number = int(self.code)
        except ValueError:
            pass

    def coded_societies(self):
        return Society.objects.filter(variablecodedvalue__coded_value=self.code)

    def __unicode__(self):
        return "%s - %s" % (self.code, self.description)

    class Meta(object):
        verbose_name = "Code"
        ordering = ("variable", "code_number", "code")


class VariableCodedValue(models.Model):
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
    variable = models.ForeignKey('VariableDescription', related_name="values")
    society = models.ForeignKey('Society', null=True)
    coded_value = models.CharField(max_length=100, db_index=True, null=False, default='.')
    code = models.ForeignKey('VariableCodeDescription', db_index=True, null=True)
    source = models.ForeignKey('Source', null=True)
    comment = models.TextField(default="")
    references = models.ManyToManyField('Source', related_name='references')
    subcase = models.TextField(default="")
    focal_year = models.CharField(max_length=10, default="")

    def get_description(self):
        return self.code.description if self.code else ''

    def __unicode__(self):
        return "%s" % self.coded_value

    class Meta(object):
        verbose_name = "Value"
        ordering = ("variable", "coded_value")
        index_together = [
            ['variable', 'society'],
            ['variable', 'coded_value'],
            ['variable', 'code'],
            ['society', 'coded_value'],
            ['society', 'code'],
        ]
        unique_together = ('variable', 'society', 'coded_value')


class Source(models.Model):
    """
    Stores references for VariableCodedValues, also for dataset sources.
    """
    # Not really sure if we should separate dataset sources from references (I
    # think we should), but since all the code has already been written with
    # this model, I won't change it yet.

    # text, because might be '1996', '1999-2001', or 'ND'
    year = models.CharField(max_length=30)
    author = models.CharField(max_length=50)
    reference = models.CharField(max_length=500)
    name = models.CharField(max_length=100, default="")

    def __unicode__(self):
        return "%s (%s)" % (self.author, self.year)

    class Meta(object):
        unique_together = ('year', 'author')


class LanguageFamily(models.Model):
    scheme = models.CharField(max_length=1, choices=CLASSIFICATION_SCHEMES, default='G')
    name = models.CharField(max_length=50, db_index=True)
    language_count = models.IntegerField(default=0, null=False)

    def update_counts(self):
        self.language_count = Language.objects.all().filter(family=self).count()
        self.save()


class Language(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    glotto_code = models.ForeignKey('GlottoCode', null=True, unique=True)
    # needs to be null=True because some glottolog languages do not have isocodes
    iso_code = models.ForeignKey('ISOCode', null=True)
    family = models.ForeignKey('LanguageFamily', null=True)

    def __unicode__(self):
        return "Language: %s, ISO Code %s, Glotto Code %s" % (
            self.name, self.iso_code, self.glotto_code)

    class Meta(object):
        verbose_name = "Language"
        unique_together = ('iso_code', 'glotto_code')


class GeographicRegion(models.Model):
    level_2_re = models.FloatField()
    count = models.FloatField()
    region_nam = models.CharField(max_length=254)
    continent = models.CharField(max_length=254)
    tdwg_code = models.IntegerField()
    geom = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return "Region: %s, Continent %s" % (self.region_nam, self.continent)


class LanguageTree(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    languages = models.ManyToManyField(to='Language')
    file = models.FileField(upload_to='language_trees', null=True)
    newick_string = models.TextField(default='')
    source = models.ForeignKey('Source', null=True)
