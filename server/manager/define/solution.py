# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""套餐定义模块
"""
from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppSolution
from fta.utils.decorator import exception_cache


class SolutionManager(object):

    def __init__(self):
        self.raw_solution_dict = self.get_solution()
        self.solution_list = self.raw_solution_dict.values()

    @exception_cache(timeout=15 * 60, ignore_argv=True)
    def get_solution(self):
        solution_list = orm_2_dict(
            session.query(FtaSolutionsAppSolution).all())
        return {str(solution['id']): solution for solution in solution_list}
