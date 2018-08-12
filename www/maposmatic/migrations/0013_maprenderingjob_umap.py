# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0012_remove_maprenderingjob_track_bbox_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprenderingjob',
            name='umap',
            field=models.FileField(null=True, blank=True, upload_to='upload/umaps/%Y/%m/%d/'),
        ),
    ]
