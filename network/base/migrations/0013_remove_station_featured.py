# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20141203_1805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='station',
            name='featured',
        ),
    ]
