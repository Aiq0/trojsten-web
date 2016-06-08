# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-08 09:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0002_auto_20160502_1646'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0009_auto_20160608_1143'),
    ]

    state_operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='n\xe1zov')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Competition', verbose_name='s\xfa\u0165a\u017e')),
            ],
            options={
                'verbose_name': 'Kateg\xf3ria',
                'verbose_name_plural': 'Kateg\xf3rie',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='n\xe1zov')),
                ('number', models.IntegerField(verbose_name='\u010d\xedslo')),
                ('description_points', models.IntegerField(default=0, verbose_name='body za popis')),
                ('source_points', models.IntegerField(default=0, verbose_name='body za program')),
                ('integer_source_points', models.BooleanField(default=True, verbose_name='celo\u010d\xedseln\xe9 body za program')),
                ('has_source', models.BooleanField(default=False, verbose_name='odovzd\xe1va sa zdroj\xe1k')),
                ('has_description', models.BooleanField(default=False, verbose_name='odovzd\xe1va sa popis')),
                ('has_testablezip', models.BooleanField(default=False, verbose_name='odovzd\xe1va sa zip na testova\u010d')),
                ('external_submit_link', models.CharField(blank=True, max_length=128, null=True, verbose_name='Odkaz na extern\xe9 odovzd\xe1vanie')),
                ('category', models.ManyToManyField(blank=True, to='contests.Category', verbose_name='kateg\xf3ria')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='opravovate\u013e')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.Round', verbose_name='kolo')),
            ],
            options={
                'verbose_name': '\xdaloha',
                'verbose_name_plural': '\xdalohy',
            },
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
