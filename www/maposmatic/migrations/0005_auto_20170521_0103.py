# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0004_maprenderingjob_track'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='track',
            field=models.FileField(null=True, upload_to=b'upload/tracks/', blank=True),
        ),
    ]
