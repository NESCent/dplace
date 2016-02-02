# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dplace_app', '0006_auto_rename_model_culturalvariable'),
    ]

    operations = [
        migrations.RenameModel('VariableCodeDescription', 'CulturalCodeDescription')
    ]
