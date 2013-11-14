from django.contrib.gis import admin

from models import *

admin.site.register(Society)
admin.site.register(Environmental, admin.GeoModelAdmin)
admin.site.register(ISOCode, admin.GeoModelAdmin)

admin.site.register(EAVariableDescription)
admin.site.register(EAVariableCodeDescription)
admin.site.register(EAVariableValue)
