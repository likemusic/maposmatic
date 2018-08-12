# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0011_auto_20170917_1747'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maprenderingjob',
            name='track_bbox_mode',
        ),
    ]
