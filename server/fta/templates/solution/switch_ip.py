# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.solution.base import BaseSolution
from fta.utils import logging
from fta.utils.context import Context

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """
    将处理的 IP 对象在故障机与备机间替换
    调用之前必须先获取过备机，确认 context.ip_bak 变量存在

    处理对象默认是故障机
    奇数次调用完后续的处理对象是备机
    偶数次调用完后续的处理对象是故障机
    """

    def run(self):
        context = Context(self.alarm_instance["id"])

        if not context.ip_bak:
            return self.set_finished(
                "failure", u"无备机 IP，请检查是否有先获取备机",
                failure_type="user_code_failure",
            )

        if context.ip != context.ip_bak:
            context.ip = context.ip_bak
        else:
            context.ip = self.alarm_instance["ip"]

        return self.set_finished("success", u"替换操作对象为备机")
