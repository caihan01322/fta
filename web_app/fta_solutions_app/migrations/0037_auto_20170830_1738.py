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
        ('fta_solutions_app', '0036_fix_solution_codename_1708301523'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmdef',
            name='add_from',
            field=models.CharField(default=b'user', max_length=10, verbose_name='\u65b9\u6848\u6765\u6e90', choices=[(b'user', '\u4eba\u5de5\u914d\u7f6e'), (b'admin', '\u7ba1\u7406\u5458\u914d\u7f6e'), (b'sys', '\u7cfb\u7edf\u63a8\u8350')]),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='module',
            field=models.TextField(default=b'', help_text='\u5197\u4f59\u5b57\u6bb5', verbose_name='Module', blank=True),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='module_names',
            field=models.TextField(default=b'', verbose_name='Module\u540d\u79f0', blank=True),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='set_names',
            field=models.TextField(default=b'', verbose_name='Set\u540d\u79f0', blank=True),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='topo_set',
            field=models.TextField(default=b'', help_text='\u5197\u4f59\u5b57\u6bb5', verbose_name='Set', blank=True),
        ),
        migrations.AlterField(
            model_name='outofscopearchive',
            name='cc_set_name',
            field=models.CharField(max_length=128, null=True, verbose_name='\u544a\u8b66\u96c6\u7fa4', db_index=True),
        ),
        migrations.AlterField(
            model_name='outofscopearchive',
            name='extra',
            field=models.TextField(max_length=255, null=True, verbose_name='\u6269\u5c55'),
        ),
        migrations.AlterField(
            model_name='outofscopearchive',
            name='status',
            field=models.CharField(default=b'new', max_length=10, verbose_name='\u72b6\u6001', choices=[(b'new', '\u65b0\u751f\u6210\u7684\uff0c\u672a\u5206\u6790\u51fa\u5efa\u8bae'), (b'suggest', '\u65b0\u751f\u6210\u7684\uff0c\u7b49\u5f85\u7528\u6237\u786e\u8ba4\u5efa\u8bae'), (b'enabled', '\u7528\u6237\u5df2\u542f\u7528\u91c7\u7eb3, \u5df2\u6dfb\u52a0\u5230AlarmDef\u8868\u4e2d'), (b'ignore', '\u7528\u6237\u5ffd\u7565\u7684,\u81ea\u6108\u5c0f\u52a9\u624b\u9875\u9762\u4e0d\u518d\u663e\u793a')]),
        ),
    ]
