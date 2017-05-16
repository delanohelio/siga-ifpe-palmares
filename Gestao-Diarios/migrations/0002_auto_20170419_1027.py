# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 13:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Gestao-Diarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
            ],
        ),
        migrations.RemoveField(
            model_name='disciplina',
            name='professor',
        ),
        migrations.AlterField(
            model_name='disciplina',
            name='turma',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='Gestao-Diarios.Turma'),
        ),
        migrations.AddField(
            model_name='diario',
            name='professor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Gestao-Diarios.Professor'),
        ),
    ]
