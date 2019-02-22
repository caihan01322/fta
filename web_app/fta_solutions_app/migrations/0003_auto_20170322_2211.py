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
        ('fta_solutions_app', '0002_auto_20170320_1959'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=255, verbose_name='\u7528\u6237')),
                ('is_guide', models.BooleanField(default=False, verbose_name='\u662f\u5426\u663e\u793a\u63a5\u5165\u6307\u5f15')),
            ],
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='failure_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5931\u8d25\u7c7b\u578b', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
    ]
