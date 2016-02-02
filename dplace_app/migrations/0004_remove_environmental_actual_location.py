# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dplace_app', '0003_remove_environmental_reported_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='environmental',
            name='actual_location',
        ),
    ]
