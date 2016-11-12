# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0002_maprenderingjob_overlay'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maprenderingjob',
            name='submitterip',
            field=models.GenericIPAddressField(),
        ),
    ]
