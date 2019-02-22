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
        ('fta_solutions_app', '0012_alarmtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='conf',
            name='description',
            field=models.TextField(default=b'', verbose_name='\u8bf4\u660e'),
        ),
        migrations.AlterField(
            model_name='incident',
            name='incident_type',
            field=models.CharField(choices=[(b'skip', '\u6210\u529f\u8df3\u8fc7'), (b'skip_approve', '\u5ba1\u6279\u8df3\u8fc7'), (b'pass', '\u6267\u884c\u8df3\u8fc7'), (b'wait', '\u6267\u884c\u4e2d\u7b49\u5f85'), (b'defense', '\u5f02\u5e38\u9632\u5fa1'), (b'relevance', '\u4e8b\u4ef6\u6c47\u96c6'), (b'trigger', '\u6536\u655b\u89e6\u53d1'), (b'collect_alarm', '\u6c47\u603b\u901a\u77e5'), (b'collect', '\u8d85\u51fa\u540e\u6c47\u603b'), (b'notify', '\u89e6\u53d1\u901a\u77e5'), (b'convergence', '\u544a\u8b66\u6536\u655b'), (b'network-attack', '\u7f51\u7edc\u653b\u51fb'), (b'network-quality', '\u7f51\u7edc\u6545\u969c'), (b'host-quality', '\u5355\u673a\u6545\u969c'), (b'analyze', '\u9884\u8bca\u65ad'), (b'universality', '\u5171\u6027\u5206\u6790')], max_length=128, blank=True, null=True, verbose_name='\u4e8b\u4ef6\u7c7b\u578b', db_index=True),
        ),
    ]
