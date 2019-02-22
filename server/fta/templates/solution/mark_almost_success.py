# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.solution.base import BaseSolution
from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import logging
from fta.utils.context import Context

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    """标注处理流程为基本成功，之后的步骤不会把整个流程变为失败状态"""

    def run(self):
        session.query(FtaSolutionsAppAlarminstance)\
            .filter_by(id=self.alarm_instance["id"])\
            .update({"status": "almost_success"})

        context = Context(self.alarm_instance["id"])
        context.is_almost_success = True

        return self.set_finished("success", u"组合套餐被标记为基本成功")
