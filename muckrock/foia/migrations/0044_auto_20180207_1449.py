# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-07 14:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foia', '0043_communicationmovelog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foiarequest',
            options={'ordering': ['title'], 'permissions': (('view_foiarequest', 'Can view this request'), ('embargo_foiarequest', 'Can embargo request to make it private'), ('embargo_perm_foiarequest', 'Can embargo a request permananently'), ('crowdfund_foiarequest', 'Can start a crowdfund campaign for the request'), ('appeal_foiarequest', 'Can appeal the requests decision'), ('thank_foiarequest', 'Can thank the FOI officer for their help'), ('flag_foiarequest', 'Can flag the request for staff attention'), ('followup_foiarequest', 'Can send a manual follow up'), ('agency_reply_foiarequest', 'Can send a direct reply'), ('upload_attachment_foiarequest', 'Can upload an attachment'), ('export_csv', 'Can export a CSV of search results'), ('zip_download', 'Can download a zip file of all communications and files')), 'verbose_name': 'FOIA Request'},
        ),
        migrations.RemoveField(
            model_name='foiafile',
            name='foia',
        ),
        migrations.AlterField(
            model_name='foiarequest',
            name='date_done',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name=b'Date response received'),
        ),
        migrations.AlterField(
            model_name='foiarequest',
            name='multirequest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='foias', to='foia.FOIAMultiRequest'),
        ),
    ]
