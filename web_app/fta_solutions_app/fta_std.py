# -*- coding:utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# 最核心的元数据 Begin-------------------------------------------------------------
# 需要同时修改 fta_solutions_app/views.py 中 solution() 方法中相关内容
SOLUTION_TYPE_CHOICES = settings.DIY_TYPE_IN_ENV + (
    ('collect', _(u'汇总')),  # 特殊类别：由 collect 进程处理，此类处理不算入自愈收益体系
    ('ijobs', _(u'作业平台')),
    ('clean', _(u'磁盘清理（适用于Linux）')),
) + settings.SOLUTION_TYPE_IN_ENV + (
    ('bk_component', _(u'直接调用蓝鲸组件')),  # 界面隐藏，作为官方通用套餐提供
    ('authorize', _(u'自动授权')),
    ('http', _(u'HTTP回调')),  # 界面隐藏，作为官方通用套餐提供
    ('mark_almost_success', _(u'标记为基本成功')),  # 界面隐藏，作为官方通用套餐提供
    ('switch_ip', _(u'后续处理对象故障机与备机互换')),  # 界面隐藏，作为官方通用套餐提供
    ('check_ping', _(u'确认主机Ping不通')),  # 界面隐藏，作为官方通用套餐提供
)

# 套餐类型按组分类
SOLUTION_TYPE_GROPS = {
    u"快捷套餐类": [('clean', _(u'磁盘清理（适用于Linux）')), ('collect', _(u'汇总'))],
    u"周边系统": [('ijobs', _(u'作业平台'))] + dict(settings.SOLUTION_TYPE_IN_ENV).items(),
}

if settings.DIY_TYPE_IN_ENV:
    SOLUTION_TYPE_GROPS[u"组合套餐类"] = list(settings.DIY_TYPE_IN_ENV)

A_TYPE = [_(u"快捷套餐类"), _(u"周边系统"), _(u"组合套餐类")]

# 创建套餐页面,界面隐藏, 作为官方通用套餐提供的套餐类型列表
NO_DISPLAY_SOLUTION_TYPE = [
    "http",
    "switch_ip",
    "check_ping",
    "mark_almost_success",
    "bk_component",
    "authorize",
]

ALARM_TYPE_ONLINE = ['leaf-biz-watchman']

SOURCE_TYPE_CHOICES = (
    ('ALERT', _(u"蓝鲸监控")),
    ('QCLOUD', _(u"腾讯云监控")),
    ('ZABBIX', _(u"Zabbix监控")),
    ('OPEN-FALCON', _(u"Open-Falcon监控")),
    ('NAGIOS', _(u"NAGIOS监控")),
    ('REST-API', _(u"REST API监控")),
) + settings.SOURCE_TYPE_IN_ENV

# 告警源页面选择
SOURCE_TYPE_PAGES_CHOICES = {
    'alert': 'ALERT',
    'zabbix': 'ZABBIX',
    'open-falcon': 'OPEN-FALCON',
    'nagios': 'NAGIOS',
    'api': 'REST-API',
    'custom': 'CUSTOM',
}
SOURCE_TYPE_PAGES_CHOICES.update(settings.SOURCE_TYPE_PAGES_IN_ENV)

SOURCE_TYPE_TIPS = {
    'ZABBIX': _(u"需要自行修改zabbix_fta_alarm.py中的对应字段"),
    'NAGIOS': _(u"需要自行修改nagios_fta_event_handler.py中的对应字段"),
    'ICINGA2': _(u"需要自行修改fta_push.py中的对应字段或重新安装"),
    'PROMETHEUS': _(u"需要自行修改alertmanager中的回调地址"),
    'OPEN-FALCON': _(u"需要自行修改templates中的callback地址字段"),
    'REST-API': _(u"需要自行修改X-Secret字段的值"),
}

SOURCE_TYPE_MSG1 = {
    'QCLOUD': _(u"集成当前正在使用的蓝鲸监控"),
    'ALERT': _(u"集成当前正在使用的蓝鲸监控"),
    'ZABBIX': _(u"集成当前正在使用的 Zabbix"),
    'OPEN-FALCON': _(u"集成当前正在使用的 Open-Falcon"),
    'NAGIOS': _(u"集成当前正在使用的 Nagios"),
    'ICINGA2': _(u"集成当前正在使用的 Icinga 2"),
    'PROMETHEUS': _(u"集成当前正在使用的 Prometheus"),
    'AWS': _(u"从AWS获取告警"),
    'EMAIL': _(u"从邮件中获取告警"),
    'REST-API': _(u"实时推送告警给自愈"),
    'CUSTOM': _(u"从企业告警API中获取告警"),

}

SOURCE_TYPE_MSG2 = {
    'QCLOUD': _(u"集成当前正在使用的腾讯云监控"),
    'ALERT': _(u"集成当前正在使用的蓝鲸监控"),
    'ZABBIX': _(u"只需2步，集成企业内部正在使用的 Zabbix"),
    'OPEN-FALCON': _(u"只需2步，集成企业内部正在使用的 Open-Falcon"),
    'NAGIOS': _(u"只需4步，集成企业内部正在使用的 Nagios"),
    'ICINGA2': _(u"只需3步，集成企业内部正在使用的 Icinga 2"),
    'PROMETHEUS': _(u"只需2步，集成企业内部正在使用的 Prometheus"),
    'AWS': _(u"接受来自AWS的告警，让云主机也能故障自愈"),
    'EMAIL': _(u"从邮件中获取告警，接入自愈更加便捷"),
    'REST-API': _(u"推送消息至REST API，兼容更多的监控产品"),
    'CUSTOM': _(u"从企业告警API中获取告警，接入自愈更加便捷"),
}

# AlarmInstance 所有状态
STATUS_CHOICES = (
    ('received', _(u'收到')),  # 已收到告警
    ('waiting', _(u'审批中')),  # 等待审批
    ('converging', _(u'收敛中')),  # 正在收敛
    ('sleep', _(u'收敛处理等待')),  # 正在收敛
    ('converged', _(u'收敛结束')),  # 正在收敛
    ('recovering', _(u'处理中')),  # 正在处理
    ('success', _(u'成功')),  # 处理成功
    ('almost_success', _(u'基本成功')),  # 主要关键步骤成功，但部分非关键步骤失败
    ('failure', _(u'失败')),  # 处理失败
    ('skipped', _(u'跳过')),  # 处理跳过
    ('for_notice', _(u'请关注')),  # 目前主要用于QoS监控时对低优先级告警主动废弃的标记状态
    ('for_reference', _(u'请参考')),
    ('shield', _(u'被屏蔽')),
    ('retrying', _(u'重试中')),
    # -- 2014.07.11 加入全新三个授权uwork人工修复的相关状态
    ('authorized', _(u'授权')),  # (走授权流程）
    ('unauthorized', _(u'未授权')),  # (然后INC按原有流程处理）
    ('checking', _(u'验收中')),  # (验收中，等待结果）
)

INEFFECTIVE = ('failure', 'received', 'recovering')  # 没有生效的自愈状态 用于图表统计

STATUS_COLOR = (
    ('received', u'primary'),
    ('waiting', u'warning'),
    ('recovering', u'primary'),
    ('success', u'success'),
    ('almost_success', u'success'),
    ('failure', u'danger'),
    ('skipped', u'success'),
    ('for_notice', u'success'),
    ('for_reference', u'success'),
)

FAILURE_TYPE_CHOICES = (
    ('user_code_failure', _(u'处理出错（未分类）')),
    ('framework_code_failure', _(u'自愈系统异常')),
    ('timeout', _(u'超时')),
    ('ijobs_failure', _(u'作业执行出错')),
    ('ijobs_create_failure', _(u'作业创建失败')),
) + settings.FAILURE_TYPE_IN_ENV + (
    ('false_alarm', _(u'误告警')),
    ('user_abort', _(u'用户终止流程')),
)

ALARM_CATEGORY_CHOICES = (
    ('default', _(u'默认')),
    ('DBA', u'DBA'),
    ('sys', _(u"系统推荐"))
)

# 最核心的元数据 End---------------------------------------------
DIMENSION_CHN = {
    "host": _(u"主机"),
    "cc_set": _(u"集群"),
    "cc_biz": _(u"业务"),
    # "process": u"进程",
    # "port": u"端口",
    "alarm_type": _(u"告警类型"),
    "solution": _(u"自愈套餐"),
}

INCIDENT_CHN = {
    "skip": _(u"成功后跳过"),
    "skip_approve": _(u"成功后跳过,失败时审批"),
    "pass": _(u"执行中跳过"),
    "wait": _(u"执行中等待"),
    "relevance": _(u"汇集相关事件"),
    "trigger": _(u"收敛后处理"),
    "notify": _(u"触发通知"),
    "collect": _(u"超出后汇总"),
}
INCIDENT_CHN.update(settings.INCIDENT_CHN_IN_ENV)

STD_DT_FORMAT = '%Y-%m-%d %H:%M:%S'  # 2014-07-15 10:14:06
ATOM_RFC3339_DT_FORMAT = '%Y-%m-%dT%H:%M:%S%z'  # 2014-08-01T11:39:12+0800

# TNM告警类型的简称
ALARM_TYPE_IN_SHORT = {
    u"字符型业务特性告警": u"字符告警",
    u"单机数值型业务特性告警": u"单机数值告警",
    u"数值型业务特性告警": u"数值告警",
    u"硬盘只读告警": u"硬盘只读",
    u"上报超时告警": u"上报超时",
    u"单机性能告警": u"单机性能",
    u"单机流量告警": u"单机流量",
}
ALARM_TYPE_FROM_SHORT = {v: k for k, v in ALARM_TYPE_IN_SHORT.iteritems()}

# JungleAlert的告警维度(dimensions)
JUNGLE_SUBJECT_TYPE = {
    "cc_set": _(u"集群"),
    "set": _(u"集群"),
    "os": _(u"系统"),
    "plat": _(u"平台"),
    "_server_": "IP",
    "_path_": _(u"路径")
}

STAR_ICON = '<i class="bk-icon icon-star-shape" style="font-size:15px"></i>'
STAR_HALF_ICON = '<i class="bk-icon icon-star-shape-half-o" style="font-size:15px"></i>'

# -------------------------- 给MongoDB用的字段 BEGIN
DEFAULT_CATEGORY = 'useful'

DIGEST_CATEGORIES = (
    'useful',  # 有效告警
    'handled',  # 被自愈处理到的告警
    'unhandled'  # 未被自愈处理的告警
)

DETAIL_CATEGORIES = (
    'received',  # 已收到告警
    'for_reference',  # 请参考
    'for_notice',  # 请关注
    'waiting',  # 等待审批
    'recovering',  # 正在处理
    'success',  # 处理成功
    'almost_success',  # 处理成功
    'failure',  # 处理失败
    'skipped'  # 处理跳过
)

ALL_CATEGORIES = DIGEST_CATEGORIES + DETAIL_CATEGORIES


def get_choices():
    return map(lambda x: (x, x), ALL_CATEGORIES)

# -------------------------- 给MongoDB用的字段 END
