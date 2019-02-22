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
        ('fta_solutions_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advicedef',
            name='subject_type',
            field=models.CharField(max_length=64, verbose_name='\u8003\u5bdf\u5bf9\u8c61', choices=[(b'host', '\u4e3b\u673a'), (b'world', '\u96c6\u7fa4')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a'), (b'analyze', '\u76f8\u5173\u4e8b\u4ef6\u5206\u6790')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a'), (b'analyze', '\u76f8\u5173\u4e8b\u4ef6\u5206\u6790')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='cc_topo_set',
            field=models.CharField(db_index=True, max_length=128, verbose_name='CC\u96c6\u7fa4', blank=True),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='solution_type',
            field=models.CharField(db_index=True, max_length=128, null=True, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a'), (b'analyze', '\u76f8\u5173\u4e8b\u4ef6\u5206\u6790')]),
        ),
        migrations.AlterField(
            model_name='solution',
            name='solution_type',
            field=models.CharField(default=b'customized', max_length=128, verbose_name='\u5957\u9910\u7c7b\u578b', choices=[(b'diy', '\u7ec4\u5408\u5957\u9910'), (b'collect', '\u6c47\u603b'), (b'ijobs', '\u4f5c\u4e1a\u5e73\u53f0'), (b'clean', '\u78c1\u76d8\u6e05\u7406\uff08\u9002\u7528\u4e8eLinux\uff09'), (b'uwork', '\u817e\u8baf\u4e91\u91cd\u542f'), (b'uwork_then_ijobs', '\u817e\u8baf\u4e91\u91cd\u542f\u6267\u884c\u4f5c\u4e1a\u5e73\u53f0'), (b'get_bak_ip', '\u83b7\u53d6\u6545\u969c\u673a\u5907\u673a'), (b'notice', '\u901a\u77e5\u6216\u5ba1\u6279'), (b'sleep', '\u6682\u505c\u7b49\u5f85'), (b'bk_component', '\u76f4\u63a5\u8c03\u7528\u84dd\u9cb8\u7ec4\u4ef6'), (b'convergence', '\u81ea\u5b9a\u4e49\u6536\u655b\u9632\u5fa1'), (b'authorize', '\u81ea\u52a8\u6388\u6743'), (b'http', 'HTTP\u56de\u8c03'), (b'mark_almost_success', '\u6807\u8bb0\u4e3a\u57fa\u672c\u6210\u529f'), (b'switch_ip', '\u540e\u7eed\u5904\u7406\u5bf9\u8c61\u6545\u969c\u673a\u4e0e\u5907\u673a\u4e92\u6362'), (b'check_ping', '\u786e\u8ba4\u4e3b\u673aPing\u4e0d\u901a'), (b'analyze', '\u76f8\u5173\u4e8b\u4ef6\u5206\u6790')]),
        ),
        migrations.AlterField(
            model_name='world',
            name='cc_set_chn_name',
            field=models.CharField(max_length=30, verbose_name='\u96c6\u7fa4 \u4e2d\u6587\u540d'),
        ),
        migrations.AlterField(
            model_name='world',
            name='cc_set_name',
            field=models.CharField(max_length=30, verbose_name='\u96c6\u7fa4 \u540d'),
        ),
        migrations.AlterField(
            model_name='world',
            name='world_id',
            field=models.CharField(max_length=30, verbose_name='\u96c6\u7fa4ID'),
        ),
    ]
