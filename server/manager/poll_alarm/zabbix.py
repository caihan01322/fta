# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from fta.poll_alarm.process import BasePollAlarm
from fta.utils import logging, monitors

logger = logging.getLogger("poll_alarm.event.zabbix")


class ZabbixEventAlarm(BasePollAlarm):
    """主动推送消息，请勿添加到POLL_LIST
    """
    SOURCE_TYPE = 'ZABBIX'

    def __init__(self, data, cc_biz_id):
        super(ZabbixEventAlarm, self).__init__()
        self.alarm = data
        self.cc_biz_id = cc_biz_id
        logger.debug('zabbix get alarm is: %s' % self.alarm)

    def pull_alarm(self):
        self.alarm_list.append(self.alarm)

    def clean_host(self, alarm):
        return alarm['ip']

    def clean_source_id(self, alarm):
        return alarm["source_id"]

    def clean_source_type(self, alarm):
        return self.SOURCE_TYPE

    def clean_source_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_type(self, alarm):
        return list(monitors.lookup_alarm_type_list(
            [alarm['alarm_type']],
            cc_biz_id=self.cc_biz_id, source_type=self.SOURCE_TYPE,
            default="zabbix.*",
        ))

    def clean_alarm_desc(self, alarm):
        return alarm['alarm_content']

    def clean_alarm_source_id(self, alarm):
        return ''

    def clean_alarm_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_attr_id(self, alarm):
        return ''

    def clean_cc_biz_id(self, alarm):
        return alarm['_CC_HOST_INFO']['ApplicationID']

    def clean_cc_topo_set(self, alarm):
        return alarm['_CC_HOST_INFO']['SetName'].split(",")

    def clean_cc_app_module(self, alarm):
        return alarm['_CC_HOST_INFO']['ModuleName'].split(",")

    def clean_cc_company_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['CompanyID']

    def clean_cc_plat_id(self, alarm):
        return alarm['_CC_COMPANY_INFO']['PlatID']
