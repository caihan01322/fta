# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""
初始化预警自愈方案
告警：ZABBIX-icmpping*
策略：30天5次【host-down-monthly】
模块：空闲机
预警自愈方案：移动到故障机模块
"""
from django.utils.translation import ugettext as _

from fta_solutions_app.models import AdviceFtaDef, AdviceDef

MODEL = AdviceFtaDef

_DATA = [{
    'cc_biz_id': 0L,
    'advice_def_id': 9L,
    'is_enabled': 1,
    'module_names': _(u"空闲机"),
    'description': _(u"内置策略"),
    'exclude': u'',
    'solution_id': 36L,
    'timeout': 40L,
    'handle_type': 'solution',
    'notify':
        u'''{
            "begin_notify_wechat":true,
            "begin_notify_mail":true,
            "begin_notify_sms":false,
            "begin_notify_im":false,
            "begin_notify_phone":false,
            "success_notify_wechat":true,
            "success_notify_mail":true,
            "success_notify_sms":false,
            "success_notify_im":false,
            "success_notify_phone":false,
            "failure_notify_wechat":true,
            "failure_notify_mail":true,
            "failure_notify_sms":false,
            "failure_notify_im":false,
            "failure_notify_phone":false,
            "to_extra":false,
            "to_role":true
        }'''
}]

DATA = []

# 更新 ZABBIpX-icmping* host-down-monthly的告警建议id
for i in _DATA:
    try:
        advice_def_id = AdviceDef.objects.get(
            check_sub_type='ZABBIX-icmpping*',
            codename='host-down-monthly',
            interval=30,
            threshold=5,
            is_enabled=1,
            cc_biz_id=0
        ).id
        k = i.copy()
        k["advice_def_id"] = advice_def_id
        DATA.append(k)
    except Exception:
        pass
