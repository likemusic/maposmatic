# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0008_maprenderingjob_track_bbox_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='submitterip',
            field=models.GenericIPAddressField(),
        ),
    ]
