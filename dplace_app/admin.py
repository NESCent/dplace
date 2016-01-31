from django.contrib.gis import admin

from dplace_app import models

admin.site.register(models.Society)
admin.site.register(models.Environmental, admin.GeoModelAdmin)
admin.site.register(models.EnvironmentalVariable)
admin.site.register(models.EnvironmentalValue)
admin.site.register(models.ISOCode, admin.GeoModelAdmin)

admin.site.register(models.VariableDescription)
admin.site.register(models.VariableCodeDescription)
admin.site.register(models.VariableCodedValue)

admin.site.register(models.Language)
admin.site.register(models.LanguageFamily)
