# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dplace_app', '0005_auto_rename_model_culturalcategory'),
    ]

    operations = [
        migrations.RenameModel('VariableDescription', 'CulturalVariable')
    ]
