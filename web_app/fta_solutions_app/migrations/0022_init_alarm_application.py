# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
初始化告警源
全业务下初始化告警源：蓝鲸监控
"""
from __future__ import unicode_literals

from django.db import migrations

from fta_solutions_app.models import AlarmApplication


def initial_alarm_application(apps, schema_editor):
    try:
        AlarmApplication.objects.update_or_create(
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
        ('fta_solutions_app', '0021_alarmapplication_activate_time'),
    ]

    operations = [
        migrations.RunPython(initial_alarm_application),
    ]
