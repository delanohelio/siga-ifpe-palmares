# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-08 16:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestao-Diarios', '0004_auto_20170508_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='diario',
            name='id',
        ),
        migrations.AlterField(
            model_name='diario',
            name='numero',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
    ]
