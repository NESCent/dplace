# -*- coding: utf-8 -*-
from django.contrib.gis.db import models

# Originally from 'iso lat long.xlsx'.  This spreadsheet contains ISO Codes and their
# Locations.  Only iso codes from the 16th edition ethnologue were present.
# Other datasets references ISO Codes that were not present in 16th ed, so now
# this is loaded from the ethnologue, and locations are annotated later if known

class ISOCode(models.Model):
    iso_code = models.CharField('ISO Code', db_index=True, max_length=3)
    location = models.PointField(null=True) # only have locations for ISO codes in 16th ed ethnologue
    # For GeoDjango, must override the manager
    objects = models.GeoManager()
    def __unicode__(self):
        return "%s (%s)" % (self.iso_code, self.location)
    class Meta:
        verbose_name = "ISO Code"

SOCIETY_SOURCES = (
    ('EA', 'EA'),
    ('EA_Korotayev', 'EA_Korotayev'),
    ('EA_Bodarenko', 'EA_Bodarenko'),
    ('Binford', 'Binford'),
)

class Society(models.Model):
    ext_id = models.CharField('External ID', unique=True, max_length=10)
    name = models.CharField('Name', db_index=True, max_length=200)
    location = models.PointField('Location',null=True)
    source = models.ForeignKey('Source', null=True)
    iso_code = models.ForeignKey('ISOCode', null=True, related_name="societies")
    language = models.ForeignKey('Language', null=True, related_name="societies")
    objects = models.GeoManager()

    def get_cultural_trait_data(self):
        """Returns the Ethnographic Atlas data for the given society"""
        values = []
        qset = self.variablecodedvalue_set.select_related('code').select_related('variable')
        for value in qset.order_by('variable__label').all():
            values.append({
                'label': value.variable.label,
                'name': value.variable.name,
                'code': value.coded_value,
                'description': value.get_description(),
            })
        return values

    def __unicode__(self):
        return "%s - %s (%s)" % (self.ext_id, self.name, self.source)
    
    class Meta:
        verbose_name_plural = "Societies"

UNIT_CHOICES = (
    ('mm','mm'),
    ('℃','℃'),
    ('mo','mo'),
    ('',''),
)

class EnvironmentalVariable(models.Model):
    name = models.CharField(max_length=50, unique=True)
    units = models.CharField(max_length=10, choices=UNIT_CHOICES)
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.units)
    class Meta:
        ordering=("name",)


class EnvironmentalValue(models.Model):
    variable = models.ForeignKey('EnvironmentalVariable', related_name="values")
    value = models.FloatField(db_index=True)
    environmental = models.ForeignKey('Environmental', related_name="values")
    source = models.ForeignKey('Source', null=True)
    
    def society(self):
        return self.environmental.society
    def __unicode__(self):
        return "%f" % self.value
    class Meta:
        ordering=("variable",)
        unique_together = (
            ('variable','environmental')
        )
        index_together = [
            ['variable','value']
        ]

class Environmental(models.Model):
    # may be EA or Binford or ... something
    society = models.ForeignKey('Society', null=True, related_name="environmentals")
    reported_location = models.PointField()
    actual_location = models.PointField()
    iso_code = models.ForeignKey('ISOCode', null=True, related_name="environmentals")
    source = models.ForeignKey('Source', null=True)

    # For GeoDjango, must override the manager
    objects = models.GeoManager()

    def __unicode__(self):
        return "%d Society: %d" % (self.id, self.society_id)
    class Meta:
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
    index_categories = models.ManyToManyField('VariableCategory', related_name='index_variables')
    niche_categories = models.ManyToManyField('VariableCategory', related_name='niche_variables')
    def coded_societies(self):
        return Society.objects.filter(variablecodedvalue__in=self.values.all())
    def __unicode__(self):
        return "%s - %s" % (self.label, self.name)
    class Meta:
        verbose_name = "Variable"
        ordering=("label",)

class VariableCategory(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering=("name",)

class VariableCodeDescription(models.Model):
    """
    Most of the variables in the Ethnographic Atlas are coded with
    discrete values that map to a text description, e.g.

        CODE: 3, DESCRIPTION: 26 - 35% Dependence

    Some coded values to not map to a description, e.g. those that
    represent a 4-digit year

    This model is not used by every value in the EA.

    """
    variable = models.ForeignKey('VariableDescription', related_name="codes", db_index=True)
    code = models.CharField(max_length=20, db_index=True, null=False, default='.')
    code_number = models.IntegerField(null=True, db_index=True)
    description = models.CharField(max_length=500, default='Unknown')
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
    class Meta:
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
    society = models.ForeignKey('Society', limit_choices_to={'source__in': [x[0] for x in SOCIETY_SOURCES]}, null=True)
    coded_value = models.CharField(max_length=100, db_index=True, null=False, default='.')
    code = models.ForeignKey('VariableCodeDescription', db_index=True, null=True)
    source = models.ForeignKey('Source', null=True)
    
    def get_description(self):
        if self.code is not None:
            return self.code.description
        else:
            return u''
    def __unicode__(self):
        return "%s" % self.coded_value
    class Meta:
        verbose_name = "Value"
        ordering = ("variable", "coded_value")
        index_together = [
            ['variable','society'],
            ['variable','coded_value'],
            ['variable','code'],
            ['society','coded_value'],
            ['society','code'],
        ]
        unique_together = (
            ('variable','society','coded_value'),
        )

class Source(models.Model):
    """
    Source information for various items in the cultural traits data sets
    """
    year = models.CharField(max_length=10) # text, because might be '1996', '1999-2001', or 'ND'
    author = models.CharField(max_length=50)
    reference = models.CharField(max_length=500)
    focal_year = models.CharField(max_length=10,null=True)
    subcase = models.CharField(max_length=32,null=True)
    def __unicode__(self):
        return "%s (%s)" % (self.author, self.year)
    class Meta:
        unique_together = (
            ('year','author')
        )

CLASS_LEVELS = (
    (1, 'Family'),
    (2, 'Subfamily'),
    (3, 'Subsubfamily')
)

class LanguageClass(models.Model):
    # max length 37
    name = models.CharField(max_length=50, db_index=True)
    level = models.IntegerField(db_index=True, choices=CLASS_LEVELS)
    parent = models.ForeignKey('self', null=True, default=None)
    language_count = models.IntegerField(default=0,null=False)
    def update_counts(self):
        if self.level == 1:
            self.language_count = self.languages1.count()
        elif self.level == 2:
            self.language_count = self.languages2.count()
        elif self.level == 3:
            self.language_count = self.languages3.count()
        self.save()
    def __unicode__(self):
        return "Language Class %s, level %d" % (self.name, self.level)
    class Meta:
        verbose_name = "Language Class"
        ordering= ('level', 'name')

CLASSIFICATION_SCHEMES = (
    ('E', 'Ethnologue17',),
    ('R', 'Ethnologue17-Revised',),
    #... any others as they become available. I can see a time in
    # the not too distant future when we'll get better ones.
)

class LanguageClassification(models.Model):
    scheme = models.CharField(max_length=1, choices=CLASSIFICATION_SCHEMES, default='E');
    language = models.ForeignKey('Language', null=True)
    # From 'Ethnologue Classification (unrevised)' column
    ethnologue_classification = models.CharField(max_length=250, db_index=True, unique=True)
    # From 'FAMILY-REVISED', 'Class2', 'Class3'
    class_family = models.ForeignKey('LanguageClass', limit_choices_to={'level': 1}, related_name="languages1", null=True)
    class_subfamily = models.ForeignKey('LanguageClass', limit_choices_to={'level': 2}, related_name="languages2", null=True)
    class_subsubfamily = models.ForeignKey('LanguageClass', limit_choices_to={'level': 3}, related_name="languages3", null=True)
    def __unicode__(self):
        return "Classification: %s for language %s" % (self.ethnologue_classification, self.language)
    class Meta:
        index_together = [
            ['class_family', 'class_subfamily', 'class_subsubfamily']
        ]
        ordering=("language__name",)

class Language(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    iso_code = models.ForeignKey('ISOCode', related_name="languages", unique=True)
    def __unicode__(self):
        return "Language: %s, ISO Code %s" % (self.name, self.iso_code.iso_code)
    class Meta:
        verbose_name = "Language"

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
    file = models.FileField(upload_to='language_trees',null=True)