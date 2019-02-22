# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.utils import simulate


class SolutionManager(object):
    """Get solution_def from DB or NET or Others"""

    def __init__(self):
        self.raw_solution_dict = self.get_solution()

    def get_solution(self):
        """
        :return dict: {solution_def_id: solution_def}
            solution_def_dict, key is solution_def's id
        """
        return simulate.get_solution()
