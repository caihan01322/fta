# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

from fta.poll_alarm.process import BasePollAlarm
from fta.utils import logging, monitors

logger = logging.getLogger("poll_alarm.event.rest_api")


class RestApiEventAlarm(BasePollAlarm):
    """
    主动推送消息，请勿添加到POLL_LIST
    {
    "application_id": "--",     // 故障自愈APP上申请的 应用ID，必须
    "ip": '10.0.0.1',      // 告警源IP，必须
    "source_id": "12345",       // 告警源的告警ID，必须
    "source_time": "12345",       // 告警发生的时间，格式：YYYY-MM-DD HH:mm:ss，必须
    "alarm_type": "ping",     // 告警类型（按业务存储，不填则统一放到默认分类下），可选
    "alarm_content": "FAILURE for production/HTTP on machine 10.0.0.1", // 告警详情，可选
    }
    """
    SOURCE_TYPE = 'REST-API'

    def __init__(self, alarm, cc_biz_id):
        """post_data数据格式规范见xxx
        """
        super(RestApiEventAlarm, self).__init__()
        self.cc_biz_id = cc_biz_id
        self.alarm = alarm
        logger.debug('rest_api get raw data is: %s' % alarm)

    def pull_alarm(self):
        """pull操作直接解析原始数据，合法添加到alarm_list
        """
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
            default="api_default",
        ))

    def clean_alarm_time(self, alarm):
        """
        获取告警时间
        :param alarm: 原始告警字典
        """
        return alarm['source_time']

    def clean_alarm_desc(self, alarm):
        return alarm['alarm_content']

    def clean_alarm_source_id(self, alarm):
        return ''

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

    def clean_alarm_context(self, alarm):
        try:
            alarm_context = json.dumps(alarm.get('alarm_context', ''))
        except BaseException:
            logger.error(u"alarm_context 解析出错:\n%s" % alarm_context)
            alarm_context = ''
        return alarm_context
