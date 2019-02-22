# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json as json_

from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppConf


class Conf(object):
    """simple way to use Conf table in MySQL"""

    @classmethod
    def get(cls, key, default_value=None, json=False):
        """get conf from db by key"""
        try:
            result = session.query(FtaSolutionsAppConf)\
                .filter_by(name=key).first().value
            if json is True:
                return json_.loads(result)
            return result
        except BaseException:
            return default_value

    @classmethod
    def set(cls, key, value):
        """set conf to db by key and value"""
        session.query(FtaSolutionsAppConf)\
            .filter_by(name=key).update({"value": value})


def get_fta_admin_str():
    """
    开发负责人，多个请以英文逗号(,)分隔
    """
    return Conf.get('FTA_ADMIN_LIST')


def get_fta_admin_list():
    """
    开发负责人列表
    """
    admin_str = get_fta_admin_str()
    return admin_str.split(',') if admin_str else []


def get_fta_boss_str():
    """
    运营负责人，多个请以英文逗号(,)分隔
    """
    return Conf.get('FTA_BOSS_LIST')


def get_fta_boss_list():
    """
    运营负责人列表
    """
    boss_str = get_fta_boss_str()
    return boss_str.split(',') if boss_str else []
