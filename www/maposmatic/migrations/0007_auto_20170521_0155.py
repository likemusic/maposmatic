# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0006_auto_20170521_0142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='track',
            field=models.FileField(null=True, upload_to=b'upload/tracks/%Y/%m/%d/', blank=True),
        ),
    ]
