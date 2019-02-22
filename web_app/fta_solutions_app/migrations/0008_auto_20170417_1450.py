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
        ('fta_solutions_app', '0007_auto_20170417_1151'),
    ]

    operations = [
        migrations.AddField(
            model_name='adviceftadef',
            name='exclude',
            field=models.TextField(default=b'', null=True, verbose_name='\u6392\u9664\u7684\u4e1a\u52a1', blank=True),
        ),
        migrations.AlterField(
            model_name='adviceftadef',
            name='cc_biz_id',
            field=models.IntegerField(help_text='0\u8868\u793a\u5168\u4e1a\u52a1', verbose_name='\u4e1a\u52a1\u7f16\u7801', db_index=True),
        ),
    ]
