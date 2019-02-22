# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
初始化微信审批配置
"""
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings

from fta_solutions_app.models import Conf


def initial_wechat_conf_data(apps, schema_editor):

    Conf.objects.update_or_create(
        name='WECHAT_APP_URL',
        defaults={
            'value': settings.WECHAT_APP_URL,
            'description': u"APP微信端地址(外网可访问)"
        }
    )
    Conf.objects.update_or_create(
        name='WECHAT_STATIC_URL',
        defaults={
            'value': settings.WECHAT_STATIC_URL,
            'description': u"APP微信端静态资源地址(外网可访问)"
        }
    )
    Conf.objects.update_or_create(
        name='WECHAT_SUPER_APPROVER',
        defaults={
            'value': '',
            'description': u"微信审批的管理员，多个请以英文逗号(,)分隔"
        }
    )
    for config in settings.WECHAT_CONFIG:
        Conf.objects.update_or_create(
            name=config['name'],
            defaults={
                'value': config['value'],
                'description': config['description']
            }
        )

    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0017_init_fixture'),
    ]

    operations = [
        migrations.RunPython(initial_wechat_conf_data),
    ]
