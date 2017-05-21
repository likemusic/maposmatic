# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import www.maposmatic.models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0005_auto_20170521_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='track',
            field=models.FileField(null=True, upload_to=www.maposmatic.models.get_track_path, blank=True),
        ),
    ]
