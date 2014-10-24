# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20141015_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transponder',
            name='alive',
            field=models.BooleanField(default=True),
        ),
    ]
