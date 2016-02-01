# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dplace_app', '0002_remove_isocode_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='environmental',
            name='reported_location',
        ),
    ]
