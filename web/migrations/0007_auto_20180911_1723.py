# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-09-11 09:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0006_auto_20180911_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='MentorGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('brief', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': '21. 导师组',
            },
        ),
        migrations.AddField(
            model_name='userinfo',
            name='role',
            field=models.SmallIntegerField(choices=[(0, '学员'), (1, '导师'), (2, '讲师'), (3, '管理员')], default=0, verbose_name='角色'),
        ),
        migrations.AddField(
            model_name='mentorgroup',
            name='mentors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
