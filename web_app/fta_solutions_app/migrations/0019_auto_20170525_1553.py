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


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0018_init_wechat_conf'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmapplication',
            name='app_method',
            field=models.CharField(default=b'GET', choices=[(b'GET', b'GET'), (b'POST', b'POST')], max_length=10, blank=True, null=True, verbose_name='\u8bf7\u6c42\u7c7b\u578b'),
        ),
        migrations.AddField(
            model_name='alarmapplication',
            name='app_url',
            field=models.TextField(default=b'', null=True, verbose_name='\u62c9\u53d6\u544a\u8b66\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='alarmapplication',
            name='source_type',
            field=models.CharField(max_length=64, verbose_name='\u544a\u8b66\u6e90\u6807\u8bc6', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'ZABBIX', b'Zabbix'), (b'NAGIOS', b'Nagios'), (b'OPEN-FALCON', b'Open-Falcon'), (b'REST-API', b'REST API'), (b'CUSTOM', '\u81ea\u5b9a\u4e49\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='source_type',
            field=models.CharField(default=b'ALERT', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API'), (b'CUSTOM', '\u81ea\u5b9a\u4e49\u76d1\u63a7')], max_length=32, blank=True, null=True, verbose_name='\u544a\u8b66\u6e90'),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='alarm_type',
            field=models.CharField(max_length=128, verbose_name='\u544a\u8b66\u7c7b\u578b', db_index=True),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'gcloud_failure', '\u6807\u51c6\u8fd0\u7ef4\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='source_id',
            field=models.CharField(max_length=255, null=True, verbose_name='\u544a\u8b66\u6e90\u7cfb\u7edf\u5185id', db_index=True),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API'), (b'CUSTOM', '\u81ea\u5b9a\u4e49\u76d1\u63a7'), (b'FTA', '\u6545\u969c\u81ea\u6108')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='failure_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5931\u8d25\u7c7b\u578b', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'gcloud_failure', '\u6807\u51c6\u8fd0\u7ef4\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90\u5934', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API'), (b'CUSTOM', '\u81ea\u5b9a\u4e49\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'gcloud_failure', '\u6807\u51c6\u8fd0\u7ef4\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7'), (b'OPEN-FALCON', 'Open-Falcon\u76d1\u63a7'), (b'NAGIOS', 'NAGIOS\u76d1\u63a7'), (b'REST-API', b'REST API'), (b'CUSTOM', '\u81ea\u5b9a\u4e49\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='solution',
            name='solution_type',
            field=models.CharField(default=b'customized', max_length=128, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'gcloud', '\u6807\u51c6\u8fd0\u7ef4\u6d41\u7a0b'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'notice_only', '\u901a\u77e5'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a')]),
        ),
    ]
