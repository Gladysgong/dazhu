# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-26 16:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ueditor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='rndName',
            field=models.CharField(max_length=150),
        ),
    ]
