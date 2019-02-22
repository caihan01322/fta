# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import traceback

from django.utils.translation import ugettext as _

from fta_solutions_app.models import AlarmType

MODEL = AlarmType

ITEM_CHECKER = lambda apps, item: not AlarmType.objects.filter(
    source_type=item['source_type'],
    cc_biz_id=item['cc_biz_id'],
    description=item['description'],
).exists()

CHECKER = lambda apps: True


def RUNNER(apps, schema_editor, module, silent):  # noqa
    for item in module.DATA:
        try:
            refs = module.MODEL.objects.filter(
                source_type=item['source_type'],
                cc_biz_id=item['cc_biz_id'],
                description=item['description'])
            refs.update(
                alarm_type=item['alarm_type'],
                pattern=item['pattern'],
                match_mode=item['match_mode'])
        except Exception:
            if not silent:
                raise
            print(traceback.format_exc())

    # 已经存在的，同步修改
    from fta_solutions_app.models import AlarmDef
    AlarmDef.objects.filter(alarm_type='ZABBIX-icmping*').update(alarm_type='ZABBIX-icmpping*')
    AlarmDef.objects.filter(alarm_type='open-falcon-.*').update(alarm_type='open-falcon.*')


DATA = [
    # ZABBIX
    {
        'alarm_type': 'ZABBIX-icmpping*',
        'cc_biz_id': 0,
        'description': _(u'Ping检查(icmpping*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'icmpping*',
        'source_type': 'ZABBIX'
    },
    # OPEN-FALCON
    {
        'alarm_type': 'open-falcon.*',
        'cc_biz_id': 0,
        'description': u'Open-falcon其他',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'open-falcon.*',
        'source_type': 'OPEN-FALCON'
    },
]
