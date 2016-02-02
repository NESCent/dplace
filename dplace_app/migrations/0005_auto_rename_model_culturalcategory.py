# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dplace_app', '0004_remove_environmental_actual_location'),
    ]

    operations = [
        migrations.RenameModel('VariableCategory', 'CulturalCategory')
    ]
