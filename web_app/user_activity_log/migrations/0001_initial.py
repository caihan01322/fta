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
            name='UserActivityLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_id', models.CharField(help_text='\u4fbf\u4e8e\u8bb0\u5f55\u591a\u8868\u64cd\u4f5c\u7684\u60c5\u51b5', max_length=32, verbose_name='\u8bb0\u5f55\u7684\u552f\u4e00\u6807\u8bc6', db_index=True)),
                ('app_code', models.CharField(help_text='\u9488\u5bf9\u84dd\u9cb8\u5e94\u7528\u8bbf\u95ee\u5e73\u53f0\u6216\u5176\u5b83\u7cfb\u7edf\uff0c\u9700\u8981\u8bb0\u5f55\u8bbf\u95ee\u7684app_code', max_length=32, verbose_name='\u5e94\u7528\u7f16\u7801')),
                ('username', models.CharField(max_length=32, verbose_name='\u7528\u6237\u540d\u79f0')),
                ('activity_type', models.IntegerField(default=1, verbose_name='\u6d3b\u52a8\u7c7b\u578b', choices=[(1, b'\xe6\x9f\xa5\xe8\xaf\xa2'), (2, b'\xe5\x88\x9b\xe5\xbb\xba'), (3, b'\xe5\x88\xa0\xe9\x99\xa4'), (4, b'\xe4\xbf\xae\xe6\x94\xb9')])),
                ('activity_name', models.CharField(help_text='\u81ea\u5b9a\u4e49\u672c\u6b21\u64cd\u4f5c\u7684\u540d\u79f0', max_length=100, verbose_name='\u6d3b\u52a8\u540d\u79f0')),
                ('request_params', models.TextField(help_text='\u8bb0\u5f55\u8bf7\u6c42\u7684\u53c2\u6570', null=True, verbose_name='\u8bf7\u6c42\u7684\u53c2\u6570', blank=True)),
                ('before_data', models.TextField(help_text='\u8bb0\u5f55\u6d3b\u52a8\u524d\u7684\u6570\u636e\uff0c\u4fbf\u4e8e\u6570\u636e\u5bf9\u8d26', null=True, verbose_name='\u6d3b\u52a8\u524d\u7684\u6570\u636e', blank=True)),
                ('after_data', models.TextField(help_text='\u8bb0\u5f55\u6d3b\u52a8\u540e\u7684\u6570\u636e\uff0c\u4fbf\u4e8e\u6570\u636e\u5bf9\u8d26', null=True, verbose_name='\u6d3b\u52a8\u540e\u7684\u6570\u636e', blank=True)),
                ('activity_time', models.DateTimeField(auto_now_add=True, verbose_name='\u6d3b\u52a8\u65f6\u95f4')),
                ('remarks', models.TextField(help_text='\u5176\u5b83\u7684\u4fe1\u606f', null=True, verbose_name='\u5176\u5b83\u4fe1\u606f', blank=True)),
            ],
            options={
                'db_table': 'user_activity_log',
                'verbose_name': '\u7528\u6237\u6d3b\u52a8\u8bb0\u5f55',
                'verbose_name_plural': '\u7528\u6237\u6d3b\u52a8\u8bb0\u5f55',
            },
        ),
    ]
