# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.utils.translation import ugettext as _

from fta_solutions_app.models import AdviceDef

MODEL = AdviceDef
_DATA = [{
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'确认主机是否存在硬件故障，需要做下线或者替换操作'),
    'threshold': 3L,
    'advice_type': u'hardware',
    'description': _(u'7天内|同一主机|产生3+条严重告警，应产生硬件待优化事件进行后续跟踪。'),
    'check_sub_type': u'ZABBIX-icmpping*,NAGIOS-ping',
    'interval': 7L,
    'codename': u'host-down-weekly',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'提单请现场确认主机硬件是否故障'),
    'threshold': 3L,
    'advice_type': u'hardware',
    'description': _(u'7天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行人工确认。'),
    'check_sub_type': u'BASE_ALARM_3',
    'interval': 7L,
    'codename': u'disk-readonly-weekly',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理'),
    'threshold': 3L,
    'advice_type': u'ops',
    'description': _(u'7天内|同一主机|产生3+条磁盘满告警，应产生运维待优化事件进行后续跟踪。'),
    'check_sub_type': u'OPEN-FALCON-open-falcon-df.*,ZABBIX-vfs.fs.*,BASE_ALARM_6',
    'interval': 7L,
    'codename': u'disk-full-weekly',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理'),
    'threshold': 5L,
    'advice_type': u'ops',
    'description': _(u'30天内|同一主机|产生5+条磁盘满告警，应产生运维待优化事件进行后续跟踪。'),
    'check_sub_type': u'OPEN-FALCON-open-falcon-df.*,ZABBIX-vfs.fs.*,BASE_ALARM_6',
    'interval': 30L,
    'codename': u'disk-full-monthly',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'1、请检查当前的磁盘清理策略确实是否需要调整\n2、确认该模块当前机型的硬盘空间是否合理'),
    'threshold': 2L,
    'advice_type': u'ops',
    'description': _(u'1天内|同一主机|产生2+条磁盘满告警，应产生运维待优化事件进行后续跟踪。'),
    'check_sub_type': u'OPEN-FALCON-open-falcon-df.*,ZABBIX-vfs.fs.*,BASE_ALARM_6',
    'interval': 1L,
    'codename': u'disk-full-daily',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'提单请现场确认主机硬件是否故障'),
    'threshold': 3L,
    'advice_type': u'hardware',
    'description': _(u'30天内|同一主机|产生3+条硬盘只读告警，应产生硬件待优化事件进行后续跟踪。'),
    'check_sub_type': u'BASE_ALARM_3',
    'interval': 30L,
    'codename': u'disk-readonly-monthly',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'提单请现场确认主机硬件是否故障'),
    'threshold': 2L,
    'advice_type': u'hardware',
    'description': _(u'1天内|同一主机|产生2+条硬盘只读告警，应产生硬件待优化事件进行人工确认。'),
    'check_sub_type': u'BASE_ALARM_3',
    'interval': 1L,
    'codename': u'disk-readonly-daily',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'确认主机是否存在硬件故障，需要做下线或者替换操作'),
    'threshold': 2L,
    'advice_type': u'hardware',
    'description': _(u'1天内|同一主机|产生2+条严重告警，应产生硬件待优化事件进行后续跟踪。'),
    'check_sub_type': u'ZABBIX-icmpping*,NAGIOS-ping',
    'interval': 1L,
    'codename': u'host-down-daily',
    'cc_biz_id': 0L
}, {
    'is_enabled': 1,
    'subject_type': u'host',
    'check_type': u'alarm',
    'advice': _(u'确认主机是否存在硬件故障，需要做下线或者替换操作'),
    'threshold': 5L,
    'advice_type': u'hardware',
    'description': _(u'30天内|同一主机|产生5+条严重告警，应产生硬件待优化事件进行后续跟踪。'),
    'check_sub_type': u'ZABBIX-icmpping*,NAGIOS-ping',
    'interval': 30L,
    'codename': u'host-down-monthly',
    'cc_biz_id': 0L
}]

DATA = []
for i in _DATA:
    for j in i["check_sub_type"].split(","):
        k = i.copy()
        k["check_sub_type"] = j
        DATA.append(k)
