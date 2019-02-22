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
    ]

    operations = [
        migrations.CreateModel(
            name='Approve',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('obj_id', models.CharField(max_length=255, null=True, verbose_name='\u5bf9\u8c61ID', blank=True)),
                ('message', models.TextField(verbose_name='\u5ba1\u6279\u4fe1\u606f')),
                ('callback_url', models.TextField(null=True, verbose_name='\u56de\u8c03URL', blank=True)),
                ('status', models.CharField(default=b'WAITING', max_length=32, verbose_name='\u7c7b\u578b', choices=[(b'WAITING', '\u7b49\u5f85'), (b'TY', '\u540c\u610f'), (b'BH', '\u9a73\u56de')])),
                ('approve_users', models.TextField(verbose_name='\u5ba1\u6279\u4eba,\u591a\u4e2a\u4ee5\u5206\u53f7\u5206\u9694')),
                ('approve_by', models.CharField(max_length=128, null=True, verbose_name='\u5ba1\u6279\u4eba', blank=True)),
                ('approve_at', models.DateTimeField(null=True, verbose_name='\u5ba1\u6279\u65f6\u95f4', blank=True)),
                ('create_at', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_at', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('extra', models.TextField(null=True, verbose_name='\u5176\u4ed6', blank=True)),
            ],
            options={
                'verbose_name': '\u6d41\u7a0b\u5ba1\u6279',
                'verbose_name_plural': '\u6d41\u7a0b\u5ba1\u6279',
            },
        ),
    ]
