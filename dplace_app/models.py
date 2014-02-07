from django.contrib.gis.db import models

# from 'iso lat long.xlsx'.
# I think this maps language codes to geographic points.  unclear what LMP means in LMP_LAT/LMP_LON
# Some points don't map to a 4326 point
class ISOCode(models.Model):
    iso_code = models.CharField('ISO Code', db_index=True, max_length=3)
    location = models.PointField()
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
        verbose_name = "Environmental Data Set"

class EAVariableDescription(models.Model):
    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=200, db_index=True)
    def __unicode__(self):
        return "%d - %s" % (self.number, self.name)
    class Meta:
        verbose_name = "Ethnographic Atlas Variable"
        ordering=("number",)

class EAVariableCodeDescription(models.Model):
    variable = models.ForeignKey('EAVariableDescription', related_name="codes")
    number = models.IntegerField() # Duplicate
    code = models.CharField(max_length=20, db_index=True)
    description = models.CharField(max_length=500)
    def __unicode__(self):
        return "%s: %s %s" % (self.variable, self.code, self.description)
    class Meta:
        verbose_name = "Ethnographic Atlas Variable Code Description"
        ordering = ("number", "code")

class EAVariableValue(models.Model):
    code = models.ForeignKey('EAVariableCodeDescription', related_name="values")
    society = models.ForeignKey('Society', related_name="values")
    def __unicode__(self):
        return "Society %d, Code: %d" % (self.society_id, self.code_id)
    class Meta:
        verbose_name = "Ethnographic Atlas Variable Coding"
        ordering = ('society', 'code')

class LanguageClass(models.Model):
    # max length 37
    name = models.CharField(max_length=50, db_index=True)
    level = models.IntegerField(db_index=True);
    def __unicode__(self):
        return "Language Class %s, level %d" % (self.name, self.level)
    class Meta:
        verbose_name = "Language Class"
        ordering= ('level', 'name')

class LanguageFamily(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    def __unicode__(self):
        return "Family: %s" % self.name
    class Meta:
        verbose_name = "Language Family"
        verbose_name_plural = "Language Families"

class LanguageClassification(models.Model):
    name = models.CharField(max_length=250, db_index=True, unique=True)
    def __unicode__(self):
        return "Classification: %s" % self.name

class Language(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    iso_code = models.ForeignKey('ISOCode', related_name="languages", unique=True)
    family = models.ForeignKey('LanguageFamily', related_name="languages")
    classification = models.ForeignKey('LanguageClassification', related_name="languages")
    class1 = models.ForeignKey('LanguageClass', limit_choices_to={'level': 1}, related_name="languages1")
    class2 = models.ForeignKey('LanguageClass', limit_choices_to={'level': 2}, related_name="languages2")
    class3 = models.ForeignKey('LanguageClass', limit_choices_to={'level': 3}, related_name="languages3")
    def __unicode__(self):
        return "Language: %s, ISO Code %s" % (self.name, self.iso_code.iso_code)
    class Meta:
        verbose_name = "Language"
