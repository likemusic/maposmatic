# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-02-15 11:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maposmatic', '0016_submitterip_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_file', models.FileField(blank=True, null=True, upload_to='upload/general/%Y/%m/%d/')),
                ('file_type', models.CharField(choices=[('gpx', 'GPX Track'), ('umap', 'UMAP Export File'), ('poi', 'POI File')], max_length=4)),
                ('job', models.ManyToManyField(to='maposmatic.MapRenderingJob')),
            ],
        ),

        migrations.RunSQL("""
        INSERT INTO maposmatic_uploadfile (uploaded_file, file_type) 
             SELECT DISTINCT track AS uploaded_file, 'gpx' AS file_type 
               FROM maposmatic_maprenderingjob 
              WHERE track <> ''
        """, 
        ),
        migrations.RunSQL("""
        INSERT INTO maposmatic_uploadfile (uploaded_file, file_type) 
             SELECT DISTINCT umap AS uploaded_file, 'umap' AS file_type 
               FROM maposmatic_maprenderingjob 
              WHERE umap <> ''
        """, 
        ),
        migrations.RunSQL("""
        INSERT INTO maposmatic_uploadfile (uploaded_file, file_type) 
             SELECT DISTINCT poi_file AS uploaded_file, 'poi' AS file_type 
               FROM maposmatic_maprenderingjob 
              WHERE poi_file <> ''
        """, 
        ),

        migrations.RunSQL("""
        INSERT INTO maposmatic_uploadfile_job (uploadfile_id, maprenderingjob_id) 
             SELECT file.id AS uploadfile_id, job.id AS maprenderingjob_id 
               FROM maposmatic_uploadfile file 
               JOIN maposmatic_maprenderingjob job 
                 ON job.track = file.uploaded_file
        """,
        ),

        migrations.RemoveField(
            model_name='maprenderingjob',
            name='poi_file',
        ),
        migrations.RemoveField(
            model_name='maprenderingjob',
            name='track',
        ),
        migrations.RemoveField(
            model_name='maprenderingjob',
            name='umap',
        ),
    ]
