# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
初始化配置数据
包括：应用负责人
"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

from fta_solutions_app.models import Conf


def initial_conf_data(apps, schema_editor):
    if settings.FTA_ADMIN_LIST:
        Conf.objects.update_or_create(
            name='FTA_ADMIN_LIST',
            defaults={
                'value': ','.join(settings.FTA_ADMIN_LIST),
                'description': u"开发负责人，多个请以英文逗号(,)分隔"
            }
        )
    if settings.FTA_BOSS_LIST:
        Conf.objects.update_or_create(
            name='FTA_BOSS_LIST',
            defaults={
                'value': ','.join(settings.FTA_BOSS_LIST),
                'description': u"运营负责人，多个请以英文逗号(,)分隔"
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0013_auto_20170509_1718'),
    ]

    operations = [
        migrations.RunPython(initial_conf_data),
    ]
