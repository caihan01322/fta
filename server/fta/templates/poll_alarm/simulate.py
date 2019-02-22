# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.poll_alarm.process import BasePollAlarm
from fta.utils import logging, simulate

logger = logging.getLogger("poll_alarm")


class PollAlarm(BasePollAlarm):
    """拉取告警, 并补充告警相关属性用于匹配"""

    def __init__(self):
        super(PollAlarm, self).__init__()

    def pull_alarm(self):
        """拉取告警"""
        self.alarm_list = simulate.get_alarms()

    def push_alarm(self):
        """推送告警进行匹配"""
        super(PollAlarm, self).push_alarm()

    # ------------- clean_xxx method will be called to get info to do matching

    def clean_source_type(self, alarm):
        """
        获取告警源
        :param alarm: 原始告警字典
        :return source_type: 告警源的名称
        """
        return "simulate"

    def clean_source_id(self, alarm):
        """
        获取告警源 ID
        :param alarm: 原始告警字典
        :return source_type: 告警源的告警 ID
        """
        return alarm["alarm_id"]

    def clean_alarm_type(self, alarm):
        """
        获取告警类型
        :param alarm: 原始告警字典
        :return alarm_type_list: 从 alarm 中获取的 alarm_type 的值
        """
        return [alarm["alarm_type"]]  # alarm_type_list

    def clean_alarm_time(self, alarm):
        """
        获取告警时间
        :param alarm: 原始告警字典
        :return alarm_time: 从 alarm 中获取的 alarm_time 的值
        """
        return alarm["create_time"]  # alarm_time

    # ------------- clean_xxx ends
