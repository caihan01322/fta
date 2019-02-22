# coding: utf-8
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.utils.translation import ugettext as _

from fta_solutions_app.models import AlarmType

MODEL = AlarmType
ITEM_CHECKER = lambda apps, item: not AlarmType.objects.filter(
    alarm_type=item["alarm_type"],
    source_type=item["source_type"],
    description=item["description"],
    cc_biz_id=0,
).exists()
CHECKER = lambda apps: True


def RUNNER(apps, schema_editor, module, silent):  # noqa
    try:
        module.MODEL.objects.filter(source_type="ALERT").delete()
    except Exception:
        pass
    for item in module.DATA:
        try:
            refs = module.MODEL.objects.filter(
                source_type=item['source_type'],
                cc_biz_id=item['cc_biz_id'],
                alarm_type=item['alarm_type'])
            if refs:
                refs.update(
                    description=item['description'])
            else:
                module.MODEL.objects.create(**item)
        except Exception:
            pass


DATA = [
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": _(u"可用物理内存"),
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
        "description": _(u"交换分区已用量"),
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
        "description": _(u"内存使用率"),
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
        "description": _(u"已用物理内存"),
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
        "description": _(u"应用内存使用量"),
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
        "description": _(u"应用内存使用率"),
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
        "description": _(u"接收字节流量"),
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
        "description": _(u"发送字节流量"),
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
        "description": _(u"发送包速率"),
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
        "description": _(u"接收包速率"),
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
        "description": _(u"established连接数"),
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
        "description": _(u"time_wait连接数"),
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
        "description": _(u"listen连接数"),
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
        "description": _(u"last_ack连接数"),
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
        "description": _(u"syn_recv连接数"),
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
        "description": _(u"syn_sent连接数"),
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
        "description": _(u"fin_wait1连接数"),
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
        "description": _(u"fin_wait2连接数"),
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
        "description": _(u"closing连接数"),
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
        "description": _(u"closed状态连接数"),
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
        "description": _(u"UDP接收包量"),
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
        "description": _(u"UDP发送包量"),
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
        "description": _(u"已用空间占比"),
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
        "description": _(u"读速率"),
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
        "description": _(u"写速率"),
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
        "description": _(u"磁盘IO使用率"),
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
        "description": _(u"5分钟平均负载（乘以100）"),
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
        "description": _(u"cpu总使用率"),
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
        "description": _(u"cpu单核使用率"),
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
        "description": _(u"Agent心跳丢失"),
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
        "description": _(u"磁盘只读"),
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
        "description": _(u"磁盘写满"),
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
        "description": _(u"Corefile产生"),
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
        "description": _(u"PING不可达告警"),
        "pattern": "base_alarm_8",
        "alarm_type": "base_alarm_8",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": _(u"进程端口"),
        "pattern": "proc_port_proc_port",
        "alarm_type": "proc_port_proc_port",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    },
    {
        "is_enabled": True,
        "match_mode": 0,
        "source_type": "ALERT",
        "description": _(u"自定义字符型"),
        "pattern": "gse_custom_event_gse_custom_event",
        "alarm_type": "gse_custom_event_gse_custom_event",
        "exclude": "",
        "is_hidden": False,
        "cc_biz_id": 0
    }
]

# 兼容老数据的兼容
JIANRONG_DATA = [_(u"CPU总使用率"), _(u"CPU单核使用率"), _(u"分析进程占用CPU"), _(u"分析进程占用内存"), _(u"空闲机池"), _(u"资源池")]
