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
        ('fta_solutions_app', '0030_auto_20170727_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmapplication',
            name='exception_max_num',
            field=models.IntegerField(default=0, help_text=b'\xe5\xbc\x82\xe5\xb8\xb8\xe6\xac\xa1\xe6\x95\xb0\xe8\xb6\x85\xe8\xbf\x87\xe8\xaf\xa5\xe9\x98\x88\xe5\x80\xbc\xe6\x97\xb6\xef\xbc\x8c\xe7\xa6\x81\xe7\x94\xa8\xe6\x94\xb9\xe7\x9b\x91\xe6\x8e\xa7\xe6\xba\x90,\xe4\xb8\xba0\xe5\x88\x99\xe8\xa1\xa8\xe7\xa4\xba\xe4\xb8\x8d\xe8\xae\xbe\xe9\x98\x88\xe5\x80\xbc', null=True, verbose_name='\u5f02\u5e38\u9608\u503c', blank=True),
        ),
        migrations.AlterField(
            model_name='alarmapplication',
            name='source_type',
            field=models.CharField(max_length=64, verbose_name='\u544a\u8b66\u6e90\u6807\u8bc6', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790')]),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='source_type',
            field=models.CharField(default=b'ALERT', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790')], max_length=32, blank=True, null=True, verbose_name='\u544a\u8b66\u6e90'),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'FTA', '\u6545\u969c\u81ea\u6108')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90\u5934', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790')]),
        ),
        migrations.RunPython(initial_alarm_application),
    ]
