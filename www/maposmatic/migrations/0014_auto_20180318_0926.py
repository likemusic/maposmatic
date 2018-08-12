# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0013_maprenderingjob_umap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='endofrendering_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='overlay',
            field=models.CharField(null=True, blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='resultmsg',
            field=models.CharField(null=True, blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='startofrendering_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
