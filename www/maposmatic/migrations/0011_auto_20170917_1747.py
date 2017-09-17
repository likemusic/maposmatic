# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0010_maprenderingjob_submittermail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='status',
            field=models.IntegerField(choices=[(0, 'Submitted'), (1, 'In progress'), (2, 'Done'), (3, 'Done w/o files'), (4, 'Cancelled')]),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='submittermail',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='track',
            field=models.FileField(upload_to='upload/tracks/%Y/%m/%d/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='maprenderingjob',
            name='track_bbox_mode',
            field=models.IntegerField(choices=[(0, 'Keep'), (1, 'Merge'), (2, 'Replace')], default=0),
        ),
    ]
