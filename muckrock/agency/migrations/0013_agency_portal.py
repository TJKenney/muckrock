# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0001_initial'),
        ('agency', '0012_auto_20171004_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='portal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agencies', to='portal.Portal'),
        ),
    ]
