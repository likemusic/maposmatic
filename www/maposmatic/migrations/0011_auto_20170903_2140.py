# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0010_maprenderingjob_submittermail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maprenderingjob',
            name='track_bbox_mode',
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='submittermail',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
