# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import unicode_literals

from django.db import migrations


def fix_advice_incident(apps, schema_editor):
    # 更新alarm_type sub_type信息
    from fta_solutions_app.models import AdviceDef
    AdviceDef.objects.filter(check_sub_type='ZABBIX-icmping*').update(check_sub_type='ZABBIX-icmpping*')

    # 更新incident rule信息
    from project.fixture import init_incident_def
    for data in init_incident_def.DATA:
        init_incident_def.MODEL.objects.filter(codename=data['codename']).update(rule=data['rule'])


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0038_alarmtype_update'),
    ]

    operations = [
        migrations.RunPython(fix_advice_incident)
    ]
