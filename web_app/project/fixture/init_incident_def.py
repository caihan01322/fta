# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from django.utils.translation import ugettext as _

from fta_solutions_app.models import IncidentDef

MODEL = IncidentDef
DATA = [
    {
        'cc_biz_id': 0L,
        'codename': u'ping_and_agent_time_out',
        'description': _(u'一系列单机异常类告警（同一起事件造成的多个告警）'),
        'exclude': u'',
        'id': 5L,
        'is_enabled': 1,
        'priority': 30L,
        'rule':
            u'''{
        "alarm_type": [
            "ZABBIX-icmpping*",
            "NAGIOS-ping",
            "BASE_ALARM_3"
        ],
        "timedelta": 5,
        "count": 1,
        "incident": "skip",
        "condition": {
            "alarm_type": [
                "ZABBIX-icmpping*",
                "NAGIOS-ping",
                "BASE_ALARM_3"
            ],
            "host": [
                "self"
            ]
        }
    }'''
    }, {
        'cc_biz_id': 0L,
        'codename': u'same_solution',
        'description': _(u'一系列处理套餐相同的告警（同一起事件造成的多个告警）'),
        'exclude': u'',
        'id': 2L,
        'is_enabled': 1,
        'priority': 50L,
        'rule':
            u'''{
        "alarm_type": [
            "ZABBIX-icmpping*",
            "NAGIOS-ping",
            "BASE_ALARM_3"
        ],
        "timedelta": 5,
        "count": 1,
        "incident": "skip",
        "condition": {
            "solution": [
                "self"
            ],
            "host": [
                "self"
            ],
            "alarm_type": [
                "ZABBIX-icmpping*",
                "NAGIOS-ping",
                "BASE_ALARM_3"
            ]
        }
    }'''
    }]
