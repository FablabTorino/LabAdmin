# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-05 17:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('labAdmin', '0005_auto_20160405_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logdoor',
            name='hour',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]