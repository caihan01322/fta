# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from fta.storage.mysql import orm_2_dict, session
from fta.storage.tables import FtaSolutionsAppAdvicedef
from fta.utils.decorator import exception_cache


class AdviceDefManager(object):

    def __init__(self):
        self.advicedef_list = self.get_advicedef()
        self.raw_advicedef_dict = {str(a['id']): a for a in self.advicedef_list}

    @exception_cache(timeout=15 * 60, ignore_argv=True)
    def get_advicedef(self):
        return orm_2_dict(
            session.query(FtaSolutionsAppAdvicedef).filter_by(is_enabled=True))
