# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0009_auto_20170701_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprenderingjob',
            name='submittermail',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
