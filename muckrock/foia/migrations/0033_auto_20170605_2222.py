# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-06-05 22:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foia', '0032_auto_20170423_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communicationopen',
            name='region',
            field=models.CharField(max_length=50),
        ),
    ]