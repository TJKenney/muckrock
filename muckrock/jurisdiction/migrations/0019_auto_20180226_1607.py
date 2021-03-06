# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-26 16:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jurisdiction', '0018_auto_20180214_1443'),
    ]

    operations = [
        migrations.CreateModel(
            name='LawYear',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[(b'Enacted', b'Enacted'), (b'Passed', b'Passed'), (b'Updated', b'Updated')], max_length=7)),
                ('year', models.PositiveSmallIntegerField()),
            ],
            options={
                'ordering': ['year'],
            },
        ),
        migrations.RemoveField(
            model_name='law',
            name='intro',
        ),
        migrations.RemoveField(
            model_name='law',
            name='summary',
        ),
        migrations.AddField(
            model_name='lawyear',
            name='law',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='years', to='jurisdiction.Law'),
        ),
    ]
