# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0014_auto_20180318_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='maptitle',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
