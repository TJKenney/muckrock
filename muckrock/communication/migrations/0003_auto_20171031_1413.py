# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-31 14:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foia', '0040_foiacommunication_hidden'),
        ('communication', '0002_auto_20171019_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortalCommunication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_datetime', models.DateTimeField()),
                ('direction', models.CharField(choices=[(b'incoming', b'Incoming'), (b'outgoing', b'Outgoing')], max_length=8)),
                ('communication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='portals', to='foia.FOIACommunication')),
            ],
        ),
        migrations.AlterField(
            model_name='faxcommunication',
            name='to_number',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faxes', to='communication.PhoneNumber'),
        ),
    ]
