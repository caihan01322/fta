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
from fta.utils.i18n import _

logger = logging.getLogger("solution")


class Solution(BaseSolution):

    def run(self):
        self.seconds = int(self.conf.get("seconds", "1"))
        self.wait_callback("end", delta_seconds=self.seconds)

    def end(self):
        return self.set_finished("success", _("Wait for %(seconds)s second(s)", seconds=self.seconds))
