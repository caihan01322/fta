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
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0033_zabbix_icmpping_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='outofscopearchive',
            name='cc_set_name',
            field=models.CharField(max_length=128, null=True, verbose_name='\u544a\u8b66\u6a21\u5757', db_index=True),
        ),
        migrations.AddField(
            model_name='outofscopearchive',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 29, 11, 22, 5, 790081), verbose_name='\u7edf\u8ba1\u5f52\u6863\u65f6\u95f4', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outofscopearchive',
            name='extra',
            field=models.TextField(max_length=255, null=True, verbose_name='\u6269\u5c55', blank=True),
        ),
        migrations.AddField(
            model_name='outofscopearchive',
            name='is_enabled',
            field=models.BooleanField(default=True, db_index=True, verbose_name='\u662f\u5426\u542f\u7528'),
        ),
        migrations.AddField(
            model_name='outofscopearchive',
            name='updated_on',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 29, 11, 22, 16, 333925), verbose_name='\u7edf\u8ba1\u66f4\u65b0\u65f6\u95f4', auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alarmapplication',
            name='source_type',
            field=models.CharField(max_length=64, verbose_name='\u544a\u8b66\u6e90\u6807\u8bc6', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'PROMETHEUS', 'PROMETHEUS\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='source_type',
            field=models.CharField(default=b'ALERT', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'PROMETHEUS', 'PROMETHEUS\u76d1\u63a7')], max_length=32, blank=True, null=True, verbose_name='\u544a\u8b66\u6e90'),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='tnm_attr_id',
            field=models.TextField(default=b'', null=True, verbose_name='\u6392\u9664\u4e1a\u52a1', blank=True),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'PROMETHEUS', 'PROMETHEUS\u76d1\u63a7'), (b'FTA', '\u6545\u969c\u81ea\u6108')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90\u5934', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'PROMETHEUS', 'PROMETHEUS\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API\xe7\x9b\x91\xe6\x8e\xa7'), (b'ICINGA2', 'ICINGA2\u76d1\u63a7'), (b'AWS', b'AWS'), (b'EMAIL', '\u90ae\u4ef6\u89e3\u6790'), (b'PROMETHEUS', 'PROMETHEUS\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='solution',
            name='solution_type',
            field=models.CharField(default=b'customized', max_length=128, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterUniqueTogether(
            name='outofscopearchive',
            unique_together=set([('cc_biz_id', 'alarm_type', 'cc_module', 'cc_set_name')]),
        ),
        migrations.RemoveField(
            model_name='outofscopearchive',
            name='alarm_id_list',
        ),
        migrations.RemoveField(
            model_name='outofscopearchive',
            name='attr_id',
        ),
        migrations.RemoveField(
            model_name='outofscopearchive',
            name='date',
        ),
        migrations.RemoveField(
            model_name='outofscopearchive',
            name='noc',
        ),
        migrations.RemoveField(
            model_name='outofscopearchive',
            name='operator',
        ),
    ]
