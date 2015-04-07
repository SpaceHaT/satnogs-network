# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_auto_20150209_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='station',
            name='last_seen',
            field=models.DateTimeField(default=datetime.datetime.utcnow(), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='satellite',
            name='updated',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='station',
            name='online',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
