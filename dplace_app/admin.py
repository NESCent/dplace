from django.contrib.gis import admin

from models import *

admin.site.register(Society)
admin.site.register(Environmental, admin.GeoModelAdmin)
admin.site.register(EnvironmentalVariable)
admin.site.register(EnvironmentalValue)
admin.site.register(ISOCode, admin.GeoModelAdmin)

admin.site.register(VariableDescription)
admin.site.register(VariableCodeDescription)
admin.site.register(VariableCodedValue)

admin.site.register(LanguageClass)
admin.site.register(LanguageClassification)
admin.site.register(Language)
