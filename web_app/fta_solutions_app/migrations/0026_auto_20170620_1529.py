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
        ('fta_solutions_app', '0025_auto_20170620_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='advice',
            name='offline_handle',
            field=models.CharField(default=b'no', max_length=32, verbose_name='\u4f18\u5316\u9879\u72b6\u6001', choices=[(b'ok', '\u5df2\u7ecf\u7ebf\u4e0b\u5904\u7406\u8be5\u98ce\u9669'), (b'no', '\u672a\u5904\u7406')]),
        ),
        migrations.AlterField(
            model_name='advice',
            name='status',
            field=models.CharField(max_length=32, verbose_name='\u4f18\u5316\u9879\u72b6\u6001'),
        ),
    ]
