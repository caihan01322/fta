# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import copy
import hashlib

from fta.poll_alarm.process import BasePollAlarm
from fta.utils import logging, monitors

logger = logging.getLogger("poll_alarm.event.openfalcon")


class OpenFalconEventAlarm(BasePollAlarm):
    """主动推送消息，请勿添加到POLL_LIST
    """
    SOURCE_TYPE = 'OPEN-FALCON'

    def __init__(self, alarm, cc_biz_id):
        """raw_data数据格式规范见xxx
        """
        super(OpenFalconEventAlarm, self).__init__()
        self.alarm = alarm
        self.cc_biz_id = cc_biz_id
        logger.debug('openfalon callback params is: %s' % alarm)

    def pull_alarm(self):
        self.alarm_list.append(self.alarm)

    def clean_host(self, alarm):
        """
        必须在agent中配置hostname为IP地址
        """
        return alarm['_CC_HOST_INFO']['InnerIP']

    def clean_source_id(self, alarm):
        # 去除影响
        alarm = copy.copy(alarm)
        alarm.pop('_CC_HOST_INFO', None)
        alarm.pop('_CC_COMPANY_INFO', None)

        params = '&'.join(['%s=%s' % (i, alarm[i]) for i in sorted(alarm)])
        return hashlib.sha1(params).hexdigest()

    def clean_source_time(self, alarm):
        return alarm['source_time']

    def clean_source_type(self, alarm):
        return self.SOURCE_TYPE

    def clean_alarm_attr_id(self, alarm):
        return ''

    def clean_alarm_source_id(self, alarm):
        return ''

    def clean_alarm_type(self, alarm):
        return list(monitors.lookup_alarm_type_list(
            [alarm['metric']],
            cc_biz_id=self.cc_biz_id, source_type=self.SOURCE_TYPE,
            default='open-falcon.*',
        ))

    def clean_alarm_time(self, alarm):
        return alarm['source_time']

    def clean_alarm_desc(self, alarm):
        """拼接描述信息
        """
        if alarm.get('tags') and alarm.get('status'):
            desc = '%s(%s/%s)' % (alarm['status'], alarm['metric'], alarm['tags'])
        elif alarm.get('status'):
            desc = '%s(%s)' % (alarm['status'], alarm['metric'])
        elif alarm.get('tags'):
            desc = '%s/%s' % (alarm['metric'], alarm['tags'])
        else:
            desc = alarm['metric']
        return desc

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
