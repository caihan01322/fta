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
    # ZABBIX
    {
        'alarm_type': 'ZABBIX-agent.*',
        'cc_biz_id': 0,
        'description': _(u'Agent状态(agent.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'agent.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-system.cpu.*',
        'cc_biz_id': 0,
        'description': _(u'CPU使用率(system.cpu.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'system.cpu.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-vm.memory.size',
        'cc_biz_id': 0,
        'description': _(u'内存使用量(vm.memory.size)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'vm.memory.size',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-system.swap.*',
        'cc_biz_id': 0,
        'description': _(u'Swap使用量(system.swap.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'system.swap.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-kernel.*',
        'cc_biz_id': 0,
        'description': _(u'系统内核状态(kernel.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'kernel.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-vfs.dev.*',
        'cc_biz_id': 0,
        'description': _(u'磁盘IO使用率(vfs.dev.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'vfs.dev.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-vfs.fs.*',
        'cc_biz_id': 0,
        'description': _(u'磁盘容量(vfs.fs.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'vfs.fs.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-proc.num',
        'cc_biz_id': 0,
        'description': _(u'进程数量检查(proc.num)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'proc.num',
        'source_type': 'ZABBIX'
    },
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
    {
        'alarm_type': 'ZABBIX-net.tcp.*',
        'cc_biz_id': 0,
        'description': _(u'TCP链接检查(net.tcp.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'net.tcp.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-net.udp.*',
        'cc_biz_id': 0,
        'description': _(u'UDP链接检查(net.udp.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'net.udp.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'ZABBIX-vfs.file.*',
        'cc_biz_id': 0,
        'description': _(u'文件状态检查(vfs.file.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'vfs.file.*',
        'source_type': 'ZABBIX'
    },
    {
        'alarm_type': 'zabbix.*',
        'cc_biz_id': 0,
        'description': _(u'Zabbix其他'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'zabbix.*',
        'source_type': 'ZABBIX'
    },
    # NAGIOS
    {
        'alarm_type': 'NAGIOS-http',
        'cc_biz_id': 0,
        'description': u'HTTP(http)',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bhttp\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-cpu',
        'cc_biz_id': 0,
        'description': u'CPU(cpu)',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bcpu\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-memory',
        'cc_biz_id': 0,
        'description': _(u'内存(memory)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bmemory\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-net',
        'cc_biz_id': 0,
        'description': _(u'网络(net)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bnet\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-filesystem',
        'cc_biz_id': 0,
        'description': _(u'文件系统(filesystem)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bfilesystem\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-disk',
        'cc_biz_id': 0,
        'description': _(u'磁盘(disk)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bdisk\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-process',
        'cc_biz_id': 0,
        'description': _(u'进程(process)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bprocess\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'NAGIOS-ping',
        'cc_biz_id': 0,
        'description': u'Ping',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bping\\b',
        'source_type': 'NAGIOS'
    },
    {
        'alarm_type': 'nagios',
        'cc_biz_id': 0,
        'description': _(u'Nagios其他(nagios)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '\\bnagios\\b',
        'source_type': 'NAGIOS'
    },
    # OPEN-FALCON
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-agent.*',
        'cc_biz_id': 0,
        'description': _(u'Agent状态(agent.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'agent.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-load.*',
        'cc_biz_id': 0,
        'description': _(u'CPU使用率(load.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'load.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-mem.*',
        'cc_biz_id': 0,
        'description': _(u'内存使用量(mem.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'mem.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-disk.io.*',
        'cc_biz_id': 0,
        'description': _(u'磁盘IO使用率(disk.io.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'disk.io.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-df.*',
        'cc_biz_id': 0,
        'description': _(u'磁盘容量(df.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'df.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-net.if.*',
        'cc_biz_id': 0,
        'description': _(u'网卡流量(net.if.*)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'net.if.*',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'OPEN-FALCON-open-falcon-net.port.listen',
        'cc_biz_id': 0,
        'description': _(u'端口监控(net.port.listen)'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'net.port.listen',
        'source_type': 'OPEN-FALCON'
    },
    {
        'alarm_type': 'open-falcon.*',
        'cc_biz_id': 0,
        'description': _(u'Open-falcon其他'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'open-falcon.*',
        'source_type': 'OPEN-FALCON'
    },
    # REST-API
    {
        'alarm_type': 'api_default',
        'cc_biz_id': 0,
        'description': _(u'REST默认分类'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'api_default',
        'source_type': 'REST-API'
    },
    # FTA
    {
        'alarm_type': 'fta_advice',
        'cc_biz_id': 0,
        'description': _(u'预警自愈'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 2,
        'pattern': 'fta_advice',
        'source_type': 'FTA'
    },
    # CUSTOM
    {
        'alarm_type': 'default',
        'cc_biz_id': 0,
        'description': _(u'默认分类'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'default',
        'source_type': 'CUSTOM'
    },
    # EMAIL
    {
        'alarm_type': 'email',
        'cc_biz_id': 0,
        'description': _(u'邮件默认'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '.*',
        'source_type': 'EMAIL'
    },
    # AWS
    {
        'alarm_type': 'AWS-CPUUtilization',
        'cc_biz_id': 0,
        'description': 'CPU Utilization',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'CPUUtilization',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-DiskReadBytes',
        'cc_biz_id': 0,
        'description': 'Disk Reads',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'DiskReadBytes',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-DiskReadOps',
        'cc_biz_id': 0,
        'description': 'Disk Read Operations',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'DiskReadOps',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-DiskWriteBytes',
        'cc_biz_id': 0,
        'description': 'Disk Writes',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'DiskWriteBytes',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-DiskWriteOps',
        'cc_biz_id': 0,
        'description': 'Disk Write Operations',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'DiskWriteOps',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-NetworkIn',
        'cc_biz_id': 0,
        'description': 'Network In',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'NetworkIn',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-NetworkOut',
        'cc_biz_id': 0,
        'description': 'Network Out',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'NetworkOut',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-StatusCheckFailed',
        'cc_biz_id': 0,
        'description': 'Status Check Failed (Any)',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'StatusCheckFailed',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-StatusCheckFailed_Instance',
        'cc_biz_id': 0,
        'description': 'Status Check Failed (Instance)',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'StatusCheckFailed_Instance',
        'source_type': 'AWS'
    },
    {
        'alarm_type': 'AWS-StatusCheckFailed_System',
        'cc_biz_id': 0,
        'description': 'Status Check Failed (System)',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 0,
        'pattern': 'StatusCheckFailed_System',
        'source_type': 'AWS'
    },
    # ICINGA2
    {
        'alarm_type': 'ping',
        'cc_biz_id': 0,
        'description': u'Ping',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^ping',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'ssh',
        'cc_biz_id': 0,
        'description': u'ssh',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^ssh',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'http',
        'cc_biz_id': 0,
        'description': u'http',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^http',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'load',
        'cc_biz_id': 0,
        'description': _(u'平均负载'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^load',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'procs',
        'cc_biz_id': 0,
        'description': _(u'进程'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^procs',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'swap',
        'cc_biz_id': 0,
        'description': u'swap',
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^swap',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'users',
        'cc_biz_id': 0,
        'description': _(u'登录用户数'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^users',
        'source_type': 'ICINGA2'
    },
    {
        'alarm_type': 'icinga',
        'cc_biz_id': 0,
        'description': _(u'icinga默认'),
        'exclude': '',
        'is_enabled': True,
        'is_hidden': False,
        'match_mode': 1,
        'pattern': '^icinga',
        'source_type': 'ICINGA2'
    },
]
