# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import random
import time

from fta.utils import logging
from mongoengine.connection import DEFAULT_CONNECTION_NAME, get_db

logger = logging.getLogger('root')


def get_cluster_alias_name(alias_name, index):
    return "%s_%s" % (alias_name, index)


class DocumentClusterMixin(object):

    RECONNECT_INTERVAL = 10
    MONGO_CONF = []

    @classmethod
    def _get_index_dict(cls):
        if not hasattr(cls, '_index_dict'):
            index_dict = {index: 0 for index in range(0, len(cls.MONGO_CONF))}
            setattr(cls, '_index_dict', index_dict)
        return cls._index_dict

    @classmethod
    def _get_db(cls):
        """Some Model using other db_alias"""
        if not cls._meta.get("db_alias"):
            return get_db(DEFAULT_CONNECTION_NAME)

        index_dict = cls._get_index_dict()
        index_list = index_dict.keys()
        random.shuffle(index_list)

        for index in index_list:

            if index_dict[index] >= time.time():
                continue
            else:
                index_dict[index] = 0

            alias_name = get_cluster_alias_name(cls._meta["db_alias"], index)
            try:
                return get_db(alias_name, reconnect=True)
            except Exception as e:
                index_dict[index] = index_dict[index] or time.time() + cls.RECONNECT_INTERVAL
                logger.warning(e)
        raise Exception("mongo all dead: %s" % cls._meta["db_alias"])
