# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-04 04:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmsitem',
            name='itemID',
            field=models.IntegerField(default=0),
        ),
    ]
