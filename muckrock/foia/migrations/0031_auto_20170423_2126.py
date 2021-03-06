# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-04-23 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foia', '0030_outboundattachment_sent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foiarequest',
            options={'ordering': ['title'], 'permissions': (('view_foiarequest', 'Can view this request'), ('embargo_foiarequest', 'Can embargo request to make it private'), ('embargo_perm_foiarequest', 'Can embargo a request permananently'), ('crowdfund_foiarequest', 'Can start a crowdfund campaign for the request'), ('appeal_foiarequest', 'Can appeal the requests decision'), ('thank_foiarequest', 'Can thank the FOI officer for their help'), ('flag_foiarequest', 'Can flag the request for staff attention'), ('followup_foiarequest', 'Can send a manual follow up'), ('agency_reply_foiarequest', 'Can send a direct reply')), 'verbose_name': 'FOIA Request'},
        ),
        migrations.AlterField(
            model_name='foiacommunication',
            name='delivered',
            field=models.CharField(blank=True, choices=[(b'fax', b'Fax'), (b'email', b'Email'), (b'mail', b'Mail'), (b'web', b'Web')], max_length=10, null=True),
        ),
    ]
