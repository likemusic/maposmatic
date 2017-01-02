# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0003_auto_20161112_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprenderingjob',
            name='bitmap_dpi',
            field=models.IntegerField(default=72),
            preserve_default=True,
        ),
    ]
