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

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """一个简易的测试"""

    def run(self):
        self.step1()
        self.wait_polling_callback(
            "step2", "http://127.0.0.1:8081/fta/status/gaze/")

    def step1(self):
        logger.info("$%s &%s run step 1",
                    self.alarm_instance["id"], self.node_idx)

    def step2(self, result):
        logger.info("$%s &%s run step 2: %s",
                    self.alarm_instance["id"], self.node_idx, result)
        import time
        time.sleep(10)
        self.wait_callback("step3", delta_seconds=10)

    def step3(self):
        logger.info("$%s &%s run step 3",
                    self.alarm_instance["id"], self.node_idx)
        return self.set_finished("success", u"执行测试套餐成功")
