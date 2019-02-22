# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta.converge.dimension import DimensionHandler
from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.i18n import _

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """可以自定义对相同 IP 相同告警类型一定时间出现一定次数后返回不同结果

    :param conf["range_count"]: 次数阈值
    :param conf["range_time"]: 时间阈值
    """

    def run(self):
        try:
            count = int(self.conf['range_count'])
            minutes = int(self.conf['range_time'])
        except BaseException:
            return self.set_finished(
                "failure", _("Configuration parameter invalid"),
                failure_type="user_code_failure",
            )

        key = "%s_%s" % (
            self.alarm_instance["alarm_type"],
            self.alarm_instance["ip"])
        condition = {
            "alarm_type": [self.alarm_instance["alarm_type"]],
            "host": [self.alarm_instance["ip"]]}
        start_timestamp = arrow.get(self.alarm_instance['source_time'])\
            .replace(minutes=-1 * minutes).replace(tzinfo="utc").timestamp

        try:
            alarm_list = DimensionHandler(
                key, condition, start_timestamp).get_by_condition()
        except BaseException:
            alarm_list = []

        if len(alarm_list) >= count:
            return self.set_finished(
                "skipped",
                _("Converged: %(count)s same type of alarms with the same IP appear within %(minites)s minute(s)",
                  count=count, minites=minutes))
        else:
            return self.set_finished("success", _("Not be converged"))
