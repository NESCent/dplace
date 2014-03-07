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
    location = models.PointField('Location')
    source = models.CharField(max_length=16,choices=SOCIETY_SOURCES)
    iso_code = models.ForeignKey('ISOCode', null=True, related_name="societies")
    
    def get_ethnographic_atlas_data(self):
        """Returns the Ethnographic Atlas data for the given society"""
        ea_values = []
        qset = self.eavariablecodedvalue_set.select_related('code').select_related('variable')
        for ea_value in qset.order_by('variable__number').all():
            ea_values.append({
                'number': ea_value.variable.number,
                'name': ea_value.variable.name,
                'code': ea_value.coded_value,
                'description': ea_value.get_description(),
            })
        return ea_values

    def __unicode__(self):
        return "%s - %s (%s)" % (self.ext_id, self.name, self.source)
    
    class Meta:
        verbose_name_plural = "Societies"

class Environmental(models.Model):
    # may be EA or Binford or ... something
    society = models.ForeignKey('Society', null=True, related_name="environmentals")
    reported_location = models.PointField()
    actual_location = models.PointField()
    iso_code = models.ForeignKey('ISOCode', null=True, related_name="environmentals")
    # Environmental data
    annual_mean_temperature = models.FloatField(null=True)
    annual_temperature_variance = models.FloatField(null=True)
    temperature_constancy = models.FloatField(null=True)
    temperature_contingency = models.FloatField(null=True)
    temperature_predictability = models.FloatField(null=True)
    annual_mean_precipitation = models.FloatField(null=True)
    annual_precipitation_variance = models.FloatField(null=True)
    precipitation_constancy = models.FloatField(null=True)
    precipitation_contingency = models.FloatField(null=True)
    precipitation_predictability = models.FloatField(null=True)
    mean_growing_season_duration = models.FloatField(null=True)
    net_primary_productivity = models.FloatField(null=True)
    bird_diversity = models.FloatField(null=True)
    mammal_diversity = models.FloatField(null=True)
    amphibian_diversity = models.FloatField(null=True)
    plant_diversity = models.FloatField(null=True)
    elevation = models.FloatField(null=True)
    slope = models.FloatField(null=True)
    # For GeoDjango, must override the manager
    objects = models.GeoManager()

    def __unicode__(self):
        return "%d Society: %d" % (self.id, self.society_id)
    class Meta:
        verbose_name = "Environmental"

class EAVariableDescription(models.Model):
    """
    Variables in the Ethnographic Atlas have a number and are accompanied
    by a description, e.g.

        NUMBER: 6, DESCRIPTION: Mode of Marriage (Primary)

    """
    number = models.IntegerField(unique=True, default=0)
    name = models.CharField(max_length=200, db_index=True, default='Unknown')
    def coded_societies(self):
        return Society.objects.filter(eavariablecodedvalue__in=self.values.all())
    def __unicode__(self):
        return "%d - %s" % (self.number, self.name)
    class Meta:
        verbose_name = "EA Variable"
        ordering=("number",)

class EAVariableCodeDescription(models.Model):
    """
    Most of the variables in the Ethnographic Atlas are coded with
    discrete values that map to a text description, e.g.

        CODE: 3, DESCRIPTION: 26 - 35% Dependence

    Some coded values to not map to a description, e.g. those that
    represent a 4-digit year

    This model is not used by every value in the EA.

    """
    variable = models.ForeignKey('EAVariableDescription', related_name="codes", db_index=True)
    code = models.CharField(max_length=20, db_index=True, null=False, default='.')
    code_number = models.IntegerField(null=True, db_index=True)
    description = models.CharField(max_length=500, default='Unknown')
    n = models.IntegerField(null=True, default=0)
    def save(self, *args, **kwargs):
        self.read_code_number()
        super(EAVariableCodeDescription, self).save(*args, **kwargs)
    def read_code_number(self):
        try:
            self.code_number = int(self.code)
        except ValueError:
            pass

    def coded_societies(self):
        return Society.objects.filter(eavariablecodedvalue__coded_value=self.code)
    def __unicode__(self):
        return "%s - %s" % (self.code, self.description)
    class Meta:
        verbose_name = "EA Code"
        ordering = ("variable", "code_number", "code")

class EAVariableCodedValue(models.Model):
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
    variable = models.ForeignKey('EAVariableDescription', related_name="values")
    society = models.ForeignKey('Society', limit_choices_to={'source__in': [x[0] for x in SOCIETY_SOURCES]}, null=True)
    coded_value = models.CharField(max_length=20, db_index=True, null=False, default='.')
    code = models.ForeignKey('EAVariableCodeDescription', db_index=True, null=True)
    def get_description(self):
        if self.code is not None:
            return self.code.description
        else:
            return u''
    def __unicode__(self):
        return "%s" % self.coded_value
    class Meta:
        verbose_name = "EA Value"
        ordering = ("variable", "coded_value")
        index_together = [
            ['variable','society'],
            ['variable','coded_value'],
            ['variable','code'],
            ['society','coded_value'],
            ['society','code'],
        ]

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

class Language(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    iso_code = models.ForeignKey('ISOCode', related_name="languages", unique=True)
    # a language might belong to a given society.
    # would be good to ask "which language does society A use" and
    # "which socieity is language A spoken in"
    # Note: This *might* need to be M2M with one language linking to multiple
    # societies and vice-versa, but I suspect this won't be common?
    society = models.ForeignKey('Society', related_name="languages", null=True)
    def __unicode__(self):
        return "Language: %s, ISO Code %s" % (self.name, self.iso_code.iso_code)
    class Meta:
        verbose_name = "Language"

