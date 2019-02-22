# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from project.poll_alarm.bk_monitor import BKMPPollAlarm


class BKMPPollAlarm1(BKMPPollAlarm):
    """
    拉取 BKMP 告警, 并补充告警相关属性用于匹配
    对于 BKMP 告警分多批次拉取防止漏拉
    这是延迟 2 分钟的批次
    """

    def __init__(self, force_begin_time=None, force_end_time=None, minutes=None, delta_minutes=0):
        super(BKMPPollAlarm1, self).__init__(
            force_begin_time, force_end_time,
            minutes=minutes - 1 if minutes else None, delta_minutes=2)
