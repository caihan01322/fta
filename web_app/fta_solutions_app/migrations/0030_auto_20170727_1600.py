# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import unicode_literals

from django.db import migrations, models

from fta_solutions_app.models import AlarmApplication


def initial_alarm_application(apps, schema_editor):
    try:
        AlarmApplication.objects.get_or_create(
            source_type='ALERT',
            cc_biz_id=0,
            defaults={
                'app_name': u"蓝鲸监控的告警源",
                'exclude': ''
            }
        )
    except Exception:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0029_auto_20170725_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmapplication',
            name='empty_begin_time',
            field=models.DateTimeField(null=True, verbose_name='\u7a7a\u544a\u8b66\u8d77\u59cb\u65f6\u95f4', blank=True),
        ),
        migrations.AddField(
            model_name='alarmapplication',
            name='empty_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u7a7a\u544a\u8b66\u6b21\u6570', blank=True),
        ),
        migrations.AddField(
            model_name='alarmapplication',
            name='exception_begin_time',
            field=models.DateTimeField(null=True, verbose_name='\u5f02\u5e38\u8d77\u59cb\u65f6\u95f4', blank=True),
        ),
        migrations.AddField(
            model_name='alarmapplication',
            name='exception_data',
            field=models.TextField(default=b'', null=True, verbose_name='\u5f02\u5e38\u4fe1\u606f', blank=True),
        ),
        migrations.AddField(
            model_name='alarmapplication',
            name='exception_num',
            field=models.IntegerField(default=0, null=True, verbose_name='\u5f02\u5e38\u6b21\u6570', blank=True),
        ),
        migrations.RunPython(initial_alarm_application),
    ]
