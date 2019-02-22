# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fta_solutions_app', '0003_auto_20170322_2211'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlarmApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source_type', models.CharField(max_length=64, verbose_name='\u544a\u8b66\u6e90\u6807\u8bc6', choices=[(b'ZABBIX', b'Zabbix'), (b'NAGIOS', b'Nagios'), (b'OPEN-FALCON', b'Open-Falcon'), (b'REST-API', b'Rest API')])),
                ('cc_biz_id', models.IntegerField(verbose_name='\u4e1a\u52a1\u7f16\u7801', db_index=True)),
                ('app_name', models.CharField(max_length=255, verbose_name='\u5e94\u7528\u540d\u79f0')),
                ('app_id', models.CharField(unique=True, max_length=255, verbose_name='\u5e94\u7528ID')),
                ('app_secret', models.CharField(unique=True, max_length=255, verbose_name='\u5e94\u7528\u5bc6\u94a5')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('create_user', models.CharField(max_length=128, verbose_name='\u521b\u5efa\u4eba')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u65f6\u95f4')),
                ('update_user', models.CharField(max_length=128, verbose_name='\u4fee\u6539\u4eba')),
                ('is_enabled', models.BooleanField(default=True, verbose_name='\u662f\u5426\u542f\u7528')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
                ('extra', models.TextField(null=True, verbose_name='\u5176\u4ed6', blank=True)),
            ],
            options={
                'verbose_name': '\u6dfb\u52a0\u544a\u8b66\u5e94\u7528',
                'verbose_name_plural': '\u6dfb\u52a0\u544a\u8b66\u5e94\u7528',
            },
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='alarm_type',
            field=models.CharField(max_length=128, verbose_name='\u544a\u8b66\u7c7b\u578b', choices=[(b'Faild_ping', 'ping\u4e0d\u53ef\u8fbe'), (b'Read_onlyDisk', '\u78c1\u76d8\u53ea\u8bfb'), (b'Agent_report_timeout', 'agent\u4e0a\u62a5\u8d85\u65f6'), (b'DiskUtilization', '\u78c1\u76d8\u5229\u7528\u7387'), (b'CPUUtilization', 'CPU\u5229\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u4f7f\u7528\u91cf'), (b'Machine_restart', '\u673a\u5668\u91cd\u542f'), (b'PublicBandwidthHigh', '\u5916\u7f51\u5e26\u5bbd\u5360\u7528\u9ad8'), (b'DiskIOAwait', '\u78c1\u76d8IO\u7b49\u5f85'), (b'DiskReadTraffic', '\u78c1\u76d8\u8bfb\u6d41\u91cf'), (b'DiskWriteTraffic', '\u78c1\u76d8\u5199\u6d41\u91cf'), (b'PublicBandwidthIn', '\u5916\u7f51\u5165\u5e26\u5bbd'), (b'PublicBandwidthOut', '\u5916\u7f51\u51fa\u5e26\u5bbd'), (b'PublicPacketsIn', '\u5916\u7f51\u5165\u5305\u91cf'), (b'PublicPacketsOut', '\u5916\u7f51\u51fa\u5305\u91cf'), (b'PublicBandwidthUtilization', '\u5916\u7f51\u5e26\u5bbd\u4f7f\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u5229\u7528\u7387'), (b'PrivateBandwidthIn', '\u5185\u7f51\u5165\u5e26\u5bbd'), (b'PrivateBandwidthOut', '\u5185\u7f51\u51fa\u5e26\u5bbd'), (b'PrivatePacketsIn', '\u5185\u7f51\u5165\u5305\u91cf'), (b'PrivatePacketsOut', '\u5185\u7f51\u51fa\u5305\u91cf'), (b'dockerCPUUtilization', 'docker\u96c6\u7fa4cpu\u5229\u7528\u7387'), (b'dockerMemoryUtilization', 'docker\u96c6\u7fa4\u5185\u5b58\u5229\u7528\u7387'), (b'cpu_3', '5\u5206\u949f\u5e73\u5747\u8d1f\u8f7d\uff08\u4e58\u4ee5100)'), (b'cpu_7', 'cpu\u603b\u4f7f\u7528\u7387'), (b'cpu_8', 'cpu\u5355\u6838\u4f7f\u7528\u7387'), (b'mem_98', '\u5e94\u7528\u7a0b\u5e8f\u4f7f\u7528\u5185\u5b58\u91cf'), (b'mem_64', '\u7269\u7406\u5185\u5b58\u4f7f\u7528\u7387'), (b'mem_97', '\u5df2\u7528\u7269\u7406\u5185\u5b58'), (b'net_10', '\u7f51\u5361\u5165\u6d41\u91cf'), (b'net_14', '\u7f51\u5361\u51fa\u6d41\u91cf'), (b'net_16', '\u7f51\u5361\u53d1\u5305\u91cf'), (b'net_20', '\u7f51\u5361\u6536\u5305\u91cf'), (b'disk_81', '\u5df2\u7528\u7a7a\u95f4\u5360\u6bd4'), (b'disk_86', '\u78c1\u76d8IO\u8bfb\u901f\u7387'), (b'disk_87', '\u78c1\u76d8IO\u5199\u901f\u7387'), (b'disk_96', '\u78c1\u76d8IO\u4f7f\u7528\u7387'), (b'BASE_ALARM_3', '\u78c1\u76d8\u53ea\u8bfb'), (b'BASE_ALARM_6', '\u78c1\u76d8\u5199\u6ee1'), (b'BASE_ALARM_7', 'Corefile\u4ea7\u751f'), (b'custom', '\u81ea\u5b9a\u4e49'), (b'agent.*', 'Agent\u72b6\u6001(agent.*)'), (b'system.cpu.*', 'CPU\u4f7f\u7528\u7387(system.cpu.*)'), (b'vm.memory.size', '\u5185\u5b58\u4f7f\u7528\u91cf(vm.memory.size)'), (b'system.swap.*', 'Swap\u4f7f\u7528\u91cf(system.swap.*)'), (b'kernel.*', '\u7cfb\u7edf\u5185\u6838\u72b6\u6001(kernel.*)'), (b'vfs.dev.*', '\u78c1\u76d8IO\u4f7f\u7528\u7387(vfs.dev.*)'), (b'vfs.fs.*', '\u78c1\u76d8\u5bb9\u91cf(vfs.fs.*)'), (b'proc.num', '\u8fdb\u7a0b\u6570\u91cf\u68c0\u67e5(proc.num)'), (b'icmping*', 'Ping\u68c0\u67e5(icmpping*)'), (b'net.tcp.*', 'TCP\u94fe\u63a5\u68c0\u67e5(net.tcp.*)'), (b'net.udp.*', 'UDP\u94fe\u63a5\u68c0\u67e5(net.udp.*)'), (b'vfs.file.*', '\u6587\u4ef6\u72b6\u6001\u68c0\u67e5(vfs.file.*)'), (b'zabbix.*', 'Zabbix\u5176\u4ed6')]),
        ),
        migrations.AlterField(
            model_name='alarmdef',
            name='source_type',
            field=models.CharField(default=b'ALERT', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7')], max_length=32, blank=True, null=True, verbose_name='\u544a\u8b66\u6e90'),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='alarm_type',
            field=models.CharField(db_index=True, max_length=128, verbose_name='\u544a\u8b66\u7c7b\u578b', choices=[(b'Faild_ping', 'ping\u4e0d\u53ef\u8fbe'), (b'Read_onlyDisk', '\u78c1\u76d8\u53ea\u8bfb'), (b'Agent_report_timeout', 'agent\u4e0a\u62a5\u8d85\u65f6'), (b'DiskUtilization', '\u78c1\u76d8\u5229\u7528\u7387'), (b'CPUUtilization', 'CPU\u5229\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u4f7f\u7528\u91cf'), (b'Machine_restart', '\u673a\u5668\u91cd\u542f'), (b'PublicBandwidthHigh', '\u5916\u7f51\u5e26\u5bbd\u5360\u7528\u9ad8'), (b'DiskIOAwait', '\u78c1\u76d8IO\u7b49\u5f85'), (b'DiskReadTraffic', '\u78c1\u76d8\u8bfb\u6d41\u91cf'), (b'DiskWriteTraffic', '\u78c1\u76d8\u5199\u6d41\u91cf'), (b'PublicBandwidthIn', '\u5916\u7f51\u5165\u5e26\u5bbd'), (b'PublicBandwidthOut', '\u5916\u7f51\u51fa\u5e26\u5bbd'), (b'PublicPacketsIn', '\u5916\u7f51\u5165\u5305\u91cf'), (b'PublicPacketsOut', '\u5916\u7f51\u51fa\u5305\u91cf'), (b'PublicBandwidthUtilization', '\u5916\u7f51\u5e26\u5bbd\u4f7f\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u5229\u7528\u7387'), (b'PrivateBandwidthIn', '\u5185\u7f51\u5165\u5e26\u5bbd'), (b'PrivateBandwidthOut', '\u5185\u7f51\u51fa\u5e26\u5bbd'), (b'PrivatePacketsIn', '\u5185\u7f51\u5165\u5305\u91cf'), (b'PrivatePacketsOut', '\u5185\u7f51\u51fa\u5305\u91cf'), (b'dockerCPUUtilization', 'docker\u96c6\u7fa4cpu\u5229\u7528\u7387'), (b'dockerMemoryUtilization', 'docker\u96c6\u7fa4\u5185\u5b58\u5229\u7528\u7387'), (b'cpu_3', '5\u5206\u949f\u5e73\u5747\u8d1f\u8f7d\uff08\u4e58\u4ee5100)'), (b'cpu_7', 'cpu\u603b\u4f7f\u7528\u7387'), (b'cpu_8', 'cpu\u5355\u6838\u4f7f\u7528\u7387'), (b'mem_98', '\u5e94\u7528\u7a0b\u5e8f\u4f7f\u7528\u5185\u5b58\u91cf'), (b'mem_64', '\u7269\u7406\u5185\u5b58\u4f7f\u7528\u7387'), (b'mem_97', '\u5df2\u7528\u7269\u7406\u5185\u5b58'), (b'net_10', '\u7f51\u5361\u5165\u6d41\u91cf'), (b'net_14', '\u7f51\u5361\u51fa\u6d41\u91cf'), (b'net_16', '\u7f51\u5361\u53d1\u5305\u91cf'), (b'net_20', '\u7f51\u5361\u6536\u5305\u91cf'), (b'disk_81', '\u5df2\u7528\u7a7a\u95f4\u5360\u6bd4'), (b'disk_86', '\u78c1\u76d8IO\u8bfb\u901f\u7387'), (b'disk_87', '\u78c1\u76d8IO\u5199\u901f\u7387'), (b'disk_96', '\u78c1\u76d8IO\u4f7f\u7528\u7387'), (b'BASE_ALARM_3', '\u78c1\u76d8\u53ea\u8bfb'), (b'BASE_ALARM_6', '\u78c1\u76d8\u5199\u6ee1'), (b'BASE_ALARM_7', 'Corefile\u4ea7\u751f'), (b'custom', '\u81ea\u5b9a\u4e49'), (b'agent.*', 'Agent\u72b6\u6001(agent.*)'), (b'system.cpu.*', 'CPU\u4f7f\u7528\u7387(system.cpu.*)'), (b'vm.memory.size', '\u5185\u5b58\u4f7f\u7528\u91cf(vm.memory.size)'), (b'system.swap.*', 'Swap\u4f7f\u7528\u91cf(system.swap.*)'), (b'kernel.*', '\u7cfb\u7edf\u5185\u6838\u72b6\u6001(kernel.*)'), (b'vfs.dev.*', '\u78c1\u76d8IO\u4f7f\u7528\u7387(vfs.dev.*)'), (b'vfs.fs.*', '\u78c1\u76d8\u5bb9\u91cf(vfs.fs.*)'), (b'proc.num', '\u8fdb\u7a0b\u6570\u91cf\u68c0\u67e5(proc.num)'), (b'icmping*', 'Ping\u68c0\u67e5(icmpping*)'), (b'net.tcp.*', 'TCP\u94fe\u63a5\u68c0\u67e5(net.tcp.*)'), (b'net.udp.*', 'UDP\u94fe\u63a5\u68c0\u67e5(net.udp.*)'), (b'vfs.file.*', '\u6587\u4ef6\u72b6\u6001\u68c0\u67e5(vfs.file.*)'), (b'zabbix.*', 'Zabbix\u5176\u4ed6')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u4e91\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstance',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='alarm_type',
            field=models.CharField(db_index=True, max_length=32, verbose_name='\u544a\u8b66\u7c7b\u578b', choices=[(b'Faild_ping', 'ping\u4e0d\u53ef\u8fbe'), (b'Read_onlyDisk', '\u78c1\u76d8\u53ea\u8bfb'), (b'Agent_report_timeout', 'agent\u4e0a\u62a5\u8d85\u65f6'), (b'DiskUtilization', '\u78c1\u76d8\u5229\u7528\u7387'), (b'CPUUtilization', 'CPU\u5229\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u4f7f\u7528\u91cf'), (b'Machine_restart', '\u673a\u5668\u91cd\u542f'), (b'PublicBandwidthHigh', '\u5916\u7f51\u5e26\u5bbd\u5360\u7528\u9ad8'), (b'DiskIOAwait', '\u78c1\u76d8IO\u7b49\u5f85'), (b'DiskReadTraffic', '\u78c1\u76d8\u8bfb\u6d41\u91cf'), (b'DiskWriteTraffic', '\u78c1\u76d8\u5199\u6d41\u91cf'), (b'PublicBandwidthIn', '\u5916\u7f51\u5165\u5e26\u5bbd'), (b'PublicBandwidthOut', '\u5916\u7f51\u51fa\u5e26\u5bbd'), (b'PublicPacketsIn', '\u5916\u7f51\u5165\u5305\u91cf'), (b'PublicPacketsOut', '\u5916\u7f51\u51fa\u5305\u91cf'), (b'PublicBandwidthUtilization', '\u5916\u7f51\u5e26\u5bbd\u4f7f\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u5229\u7528\u7387'), (b'PrivateBandwidthIn', '\u5185\u7f51\u5165\u5e26\u5bbd'), (b'PrivateBandwidthOut', '\u5185\u7f51\u51fa\u5e26\u5bbd'), (b'PrivatePacketsIn', '\u5185\u7f51\u5165\u5305\u91cf'), (b'PrivatePacketsOut', '\u5185\u7f51\u51fa\u5305\u91cf'), (b'dockerCPUUtilization', 'docker\u96c6\u7fa4cpu\u5229\u7528\u7387'), (b'dockerMemoryUtilization', 'docker\u96c6\u7fa4\u5185\u5b58\u5229\u7528\u7387'), (b'cpu_3', '5\u5206\u949f\u5e73\u5747\u8d1f\u8f7d\uff08\u4e58\u4ee5100)'), (b'cpu_7', 'cpu\u603b\u4f7f\u7528\u7387'), (b'cpu_8', 'cpu\u5355\u6838\u4f7f\u7528\u7387'), (b'mem_98', '\u5e94\u7528\u7a0b\u5e8f\u4f7f\u7528\u5185\u5b58\u91cf'), (b'mem_64', '\u7269\u7406\u5185\u5b58\u4f7f\u7528\u7387'), (b'mem_97', '\u5df2\u7528\u7269\u7406\u5185\u5b58'), (b'net_10', '\u7f51\u5361\u5165\u6d41\u91cf'), (b'net_14', '\u7f51\u5361\u51fa\u6d41\u91cf'), (b'net_16', '\u7f51\u5361\u53d1\u5305\u91cf'), (b'net_20', '\u7f51\u5361\u6536\u5305\u91cf'), (b'disk_81', '\u5df2\u7528\u7a7a\u95f4\u5360\u6bd4'), (b'disk_86', '\u78c1\u76d8IO\u8bfb\u901f\u7387'), (b'disk_87', '\u78c1\u76d8IO\u5199\u901f\u7387'), (b'disk_96', '\u78c1\u76d8IO\u4f7f\u7528\u7387'), (b'BASE_ALARM_3', '\u78c1\u76d8\u53ea\u8bfb'), (b'BASE_ALARM_6', '\u78c1\u76d8\u5199\u6ee1'), (b'BASE_ALARM_7', 'Corefile\u4ea7\u751f'), (b'custom', '\u81ea\u5b9a\u4e49'), (b'agent.*', 'Agent\u72b6\u6001(agent.*)'), (b'system.cpu.*', 'CPU\u4f7f\u7528\u7387(system.cpu.*)'), (b'vm.memory.size', '\u5185\u5b58\u4f7f\u7528\u91cf(vm.memory.size)'), (b'system.swap.*', 'Swap\u4f7f\u7528\u91cf(system.swap.*)'), (b'kernel.*', '\u7cfb\u7edf\u5185\u6838\u72b6\u6001(kernel.*)'), (b'vfs.dev.*', '\u78c1\u76d8IO\u4f7f\u7528\u7387(vfs.dev.*)'), (b'vfs.fs.*', '\u78c1\u76d8\u5bb9\u91cf(vfs.fs.*)'), (b'proc.num', '\u8fdb\u7a0b\u6570\u91cf\u68c0\u67e5(proc.num)'), (b'icmping*', 'Ping\u68c0\u67e5(icmpping*)'), (b'net.tcp.*', 'TCP\u94fe\u63a5\u68c0\u67e5(net.tcp.*)'), (b'net.udp.*', 'UDP\u94fe\u63a5\u68c0\u67e5(net.udp.*)'), (b'vfs.file.*', '\u6587\u4ef6\u72b6\u6001\u68c0\u67e5(vfs.file.*)'), (b'zabbix.*', 'Zabbix\u5176\u4ed6')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='failure_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5931\u8d25\u7c7b\u578b', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u4e91\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancearchive',
            name='source_type',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90\u5934', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='alarm_type',
            field=models.CharField(db_index=True, max_length=128, verbose_name='\u544a\u8b66\u7c7b\u578b', choices=[(b'Faild_ping', 'ping\u4e0d\u53ef\u8fbe'), (b'Read_onlyDisk', '\u78c1\u76d8\u53ea\u8bfb'), (b'Agent_report_timeout', 'agent\u4e0a\u62a5\u8d85\u65f6'), (b'DiskUtilization', '\u78c1\u76d8\u5229\u7528\u7387'), (b'CPUUtilization', 'CPU\u5229\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u4f7f\u7528\u91cf'), (b'Machine_restart', '\u673a\u5668\u91cd\u542f'), (b'PublicBandwidthHigh', '\u5916\u7f51\u5e26\u5bbd\u5360\u7528\u9ad8'), (b'DiskIOAwait', '\u78c1\u76d8IO\u7b49\u5f85'), (b'DiskReadTraffic', '\u78c1\u76d8\u8bfb\u6d41\u91cf'), (b'DiskWriteTraffic', '\u78c1\u76d8\u5199\u6d41\u91cf'), (b'PublicBandwidthIn', '\u5916\u7f51\u5165\u5e26\u5bbd'), (b'PublicBandwidthOut', '\u5916\u7f51\u51fa\u5e26\u5bbd'), (b'PublicPacketsIn', '\u5916\u7f51\u5165\u5305\u91cf'), (b'PublicPacketsOut', '\u5916\u7f51\u51fa\u5305\u91cf'), (b'PublicBandwidthUtilization', '\u5916\u7f51\u5e26\u5bbd\u4f7f\u7528\u7387'), (b'MemoryUtilization', '\u5185\u5b58\u5229\u7528\u7387'), (b'PrivateBandwidthIn', '\u5185\u7f51\u5165\u5e26\u5bbd'), (b'PrivateBandwidthOut', '\u5185\u7f51\u51fa\u5e26\u5bbd'), (b'PrivatePacketsIn', '\u5185\u7f51\u5165\u5305\u91cf'), (b'PrivatePacketsOut', '\u5185\u7f51\u51fa\u5305\u91cf'), (b'dockerCPUUtilization', 'docker\u96c6\u7fa4cpu\u5229\u7528\u7387'), (b'dockerMemoryUtilization', 'docker\u96c6\u7fa4\u5185\u5b58\u5229\u7528\u7387'), (b'cpu_3', '5\u5206\u949f\u5e73\u5747\u8d1f\u8f7d\uff08\u4e58\u4ee5100)'), (b'cpu_7', 'cpu\u603b\u4f7f\u7528\u7387'), (b'cpu_8', 'cpu\u5355\u6838\u4f7f\u7528\u7387'), (b'mem_98', '\u5e94\u7528\u7a0b\u5e8f\u4f7f\u7528\u5185\u5b58\u91cf'), (b'mem_64', '\u7269\u7406\u5185\u5b58\u4f7f\u7528\u7387'), (b'mem_97', '\u5df2\u7528\u7269\u7406\u5185\u5b58'), (b'net_10', '\u7f51\u5361\u5165\u6d41\u91cf'), (b'net_14', '\u7f51\u5361\u51fa\u6d41\u91cf'), (b'net_16', '\u7f51\u5361\u53d1\u5305\u91cf'), (b'net_20', '\u7f51\u5361\u6536\u5305\u91cf'), (b'disk_81', '\u5df2\u7528\u7a7a\u95f4\u5360\u6bd4'), (b'disk_86', '\u78c1\u76d8IO\u8bfb\u901f\u7387'), (b'disk_87', '\u78c1\u76d8IO\u5199\u901f\u7387'), (b'disk_96', '\u78c1\u76d8IO\u4f7f\u7528\u7387'), (b'BASE_ALARM_3', '\u78c1\u76d8\u53ea\u8bfb'), (b'BASE_ALARM_6', '\u78c1\u76d8\u5199\u6ee1'), (b'BASE_ALARM_7', 'Corefile\u4ea7\u751f'), (b'custom', '\u81ea\u5b9a\u4e49'), (b'agent.*', 'Agent\u72b6\u6001(agent.*)'), (b'system.cpu.*', 'CPU\u4f7f\u7528\u7387(system.cpu.*)'), (b'vm.memory.size', '\u5185\u5b58\u4f7f\u7528\u91cf(vm.memory.size)'), (b'system.swap.*', 'Swap\u4f7f\u7528\u91cf(system.swap.*)'), (b'kernel.*', '\u7cfb\u7edf\u5185\u6838\u72b6\u6001(kernel.*)'), (b'vfs.dev.*', '\u78c1\u76d8IO\u4f7f\u7528\u7387(vfs.dev.*)'), (b'vfs.fs.*', '\u78c1\u76d8\u5bb9\u91cf(vfs.fs.*)'), (b'proc.num', '\u8fdb\u7a0b\u6570\u91cf\u68c0\u67e5(proc.num)'), (b'icmping*', 'Ping\u68c0\u67e5(icmpping*)'), (b'net.tcp.*', 'TCP\u94fe\u63a5\u68c0\u67e5(net.tcp.*)'), (b'net.udp.*', 'UDP\u94fe\u63a5\u68c0\u67e5(net.udp.*)'), (b'vfs.file.*', '\u6587\u4ef6\u72b6\u6001\u68c0\u67e5(vfs.file.*)'), (b'zabbix.*', 'Zabbix\u5176\u4ed6')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='failure_type',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='\u5931\u8d25\u539f\u56e0', choices=[(b'user_code_failure', '\u5904\u7406\u51fa\u9519\uff08\u672a\u5206\u7c7b\uff09'), (b'framework_code_failure', '\u81ea\u6108\u7cfb\u7edf\u5f02\u5e38'), (b'timeout', '\u8d85\u65f6'), (b'ijobs_failure', '\u4f5c\u4e1a\u6267\u884c\u51fa\u9519'), (b'ijobs_create_failure', '\u4f5c\u4e1a\u521b\u5efa\u5931\u8d25'), (b'uwork_failure', '\u817e\u8baf\u4e91\u91cd\u542f\u8c03\u7528\u51fa\u9519'), (b'false_alarm', '\u8bef\u544a\u8b66'), (b'user_abort', '\u7528\u6237\u7ec8\u6b62\u6d41\u7a0b')]),
        ),
        migrations.AlterField(
            model_name='alarminstancebackup',
            name='source_type',
            field=models.CharField(max_length=32, null=True, verbose_name='\u544a\u8b66\u6e90', choices=[(b'ALERT', '\u84dd\u9cb8\u76d1\u63a7'), (b'QCLOUD', '\u817e\u8baf\u4e91\u76d1\u63a7'), (b'ZABBIX', 'Zabbix\u76d1\u63a7')]),
        ),
    ]
