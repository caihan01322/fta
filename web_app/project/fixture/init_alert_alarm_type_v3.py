# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""更新蓝鲸监控告警类型
2018-04-28
"""
from django.utils.translation import ugettext as _

from fta_solutions_app.models import AlarmType

MODEL = AlarmType


def RUNNER(apps, schema_editor, module, silent):  # noqa
    # 先删除所有的蓝鲸监控告警类型
    try:
        module.MODEL.objects.filter(source_type='ALERT').delete()
    except Exception:
        pass
    for item in module.DATA:
        try:
            module.MODEL.objects.create(**item)
        except Exception:
            pass


DATA = [
    {
        'alarm_type': 'custom',
        'cc_biz_id': 0,
        'description': '自定义',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'custom',
        'source_type': 'ALERT'
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "可用物理内存",
        "pattern": "mem_60",
        "alarm_type": "mem_60",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "交换分区使用量",
        "pattern": "mem_63",
        "alarm_type": "mem_63",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "物理内存使用率",
        "pattern": "mem_64",
        "alarm_type": "mem_64",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "物理内存使用量",
        "pattern": "mem_97",
        "alarm_type": "mem_97",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "应用内存使用量",
        "pattern": "mem_98",
        "alarm_type": "mem_98",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "应用内存使用率",
        "pattern": "mem_99",
        "alarm_type": "mem_99",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "接收字节流量",
        "pattern": "net_10",
        "alarm_type": "net_10",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "发送字节流量",
        "pattern": "net_14",
        "alarm_type": "net_14",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "发送包速率",
        "pattern": "net_16",
        "alarm_type": "net_16",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "接收包速率",
        "pattern": "net_20",
        "alarm_type": "net_20",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "ESTABLISHED连接数",
        "pattern": "net_110",
        "alarm_type": "net_110",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "TIME_WAIT连接数",
        "pattern": "net_111",
        "alarm_type": "net_111",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "LISTEN连接数",
        "pattern": "net_112",
        "alarm_type": "net_112",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "LAST_ACK连接数",
        "pattern": "net_113",
        "alarm_type": "net_113",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "SYN_RECV连接数",
        "pattern": "net_114",
        "alarm_type": "net_114",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "SYN_SENT连接数",
        "pattern": "net_115",
        "alarm_type": "net_115",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "FIN_WAIT1连接数",
        "pattern": "net_116",
        "alarm_type": "net_116",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "FIN_WAIT2连接数",
        "pattern": "net_117",
        "alarm_type": "net_117",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "CLOSING连接数",
        "pattern": "net_118",
        "alarm_type": "net_118",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "CLOSED状态连接数",
        "pattern": "net_119",
        "alarm_type": "net_119",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "UDP接收包量",
        "pattern": "net_120",
        "alarm_type": "net_120",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "UDP发送包量",
        "pattern": "net_121",
        "alarm_type": "net_121",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "磁盘使用率",
        "pattern": "disk_81",
        "alarm_type": "disk_81",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "读速率",
        "pattern": "disk_86",
        "alarm_type": "disk_86",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "写速率",
        "pattern": "disk_87",
        "alarm_type": "disk_87",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "磁盘IO使用率",
        "pattern": "disk_96",
        "alarm_type": "disk_96",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "5分钟平均负载",
        "pattern": "cpu_3",
        "alarm_type": "cpu_3",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "CPU总使用率",
        "pattern": "cpu_7",
        "alarm_type": "cpu_7",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "CPU单核使用率",
        "pattern": "cpu_8",
        "alarm_type": "cpu_8",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "机器重启",
        "pattern": "base_alarm_0",
        "alarm_type": "base_alarm_0",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "时间不同步",
        "pattern": "base_alarm_1",
        "alarm_type": "base_alarm_1",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "Agent心跳丢失",
        "pattern": "base_alarm_2",
        "alarm_type": "base_alarm_2",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "磁盘只读",
        "pattern": "base_alarm_3",
        "alarm_type": "base_alarm_3",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "端口未打开",
        "pattern": "base_alarm_4",
        "alarm_type": "base_alarm_4",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "进程告警",
        "pattern": "base_alarm_5",
        "alarm_type": "base_alarm_5",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "磁盘写满",
        "pattern": "base_alarm_6",
        "alarm_type": "base_alarm_6",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "Corefile产生",
        "pattern": "base_alarm_7",
        "alarm_type": "base_alarm_7",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": "PING不可达告警",
        "pattern": "base_alarm_8",
        "alarm_type": "base_alarm_8",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    }
]

# 兼容老数据的兼容
"""
新版本/老版本

交换分区使用量/交换分区已用量
物理内存使用率/内存使用率
物理内存使用量/已用物理内存
已用空间占比/磁盘使用率
5分钟平均负载（乘以100）/5分钟平均负载
机器重启/无？
时间不同步/无？
端口未打开/无？
进程告警/无？

ESTABLISHED连接数/established连接数
TIME_WAIT连接数/time_wait连接数
LISTEN连接数/listen连接数
LAST_ACK连接数/last_ack连接数
SYN_RECV连接数/syn_recv连接数
SYN_SENT连接数/syn_sent连接数
FIN_WAIT2连接数/fin_wait1连接数
FIN_WAIT2连接数/fin_wait2连接数
closing连接数/CLOSING连接数
closed状态连接数/CLOSED状态连接数
"""
JIANRONG_DATA = [_(u"交换分区使用量"), _(u"物理内存使用率"), _(u"物理内存使用量"), _(u"ESTABLISHED连接数"), _(u"TIME_WAIT连接数"),
                 _(u"LISTEN连接数"), _(u"LAST_ACK连接数"), _(u"SYN_RECV连接数"), _(u"SYN_SENT连接数"), _(u"FIN_WAIT1连接数"),
                 _(u"FIN_WAIT2连接数"), _(u"CLOSING连接数"), _(u"CLOSED状态连接数"), _(u"磁盘使用率"), _(u"5分钟平均负载"),
                 _(u"机器重启"), _(u"时间不同步"), _(u"端口未打开"), _(u"进程告警")
                 ]
