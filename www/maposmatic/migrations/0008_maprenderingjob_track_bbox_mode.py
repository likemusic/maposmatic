# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0007_auto_20170521_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprenderingjob',
            name='track_bbox_mode',
            field=models.IntegerField(default=0, choices=[(0, b'Keep'), (1, b'Merge'), (2, b'Replace')]),
        ),
    ]
