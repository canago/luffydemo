# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-09-11 11:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20180911_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponrecord',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.Order', verbose_name='关联订单'),
        ),
    ]
