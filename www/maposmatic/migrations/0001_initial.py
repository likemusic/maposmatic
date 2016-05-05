# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MapRenderingJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maptitle', models.CharField(max_length=256)),
                ('stylesheet', models.CharField(max_length=256)),
                ('layout', models.CharField(max_length=256)),
                ('paper_width_mm', models.IntegerField()),
                ('paper_height_mm', models.IntegerField()),
                ('administrative_city', models.CharField(max_length=256, blank=True)),
                ('administrative_osmid', models.IntegerField(null=True, blank=True)),
                ('lat_upper_left', models.FloatField(null=True, blank=True)),
                ('lon_upper_left', models.FloatField(null=True, blank=True)),
                ('lat_bottom_right', models.FloatField(null=True, blank=True)),
                ('lon_bottom_right', models.FloatField(null=True, blank=True)),
                ('status', models.IntegerField(choices=[(0, b'Submitted'), (1, b'In progress'), (2, b'Done'), (3, b'Done w/o files'), (4, b'Cancelled')])),
                ('submission_time', models.DateTimeField(auto_now_add=True)),
                ('startofrendering_time', models.DateTimeField(null=True)),
                ('endofrendering_time', models.DateTimeField(null=True)),
                ('resultmsg', models.CharField(max_length=256, null=True)),
                ('submitterip', models.IPAddressField()),
                ('index_queue_at_submission', models.IntegerField()),
                ('map_language', models.CharField(max_length=16)),
                ('nonce', models.CharField(max_length=16, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
