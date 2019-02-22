# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import logging
import uuid

from .django_conf import REDIS_CONF

logger = logging.getLogger('root')

# Redis链接
try:
    import redis

    redisdb_pool = redis.BlockingConnectionPool(**REDIS_CONF)
    redisdb = redis.Redis(connection_pool=redisdb_pool)
except Exception:
    redisdb = None


def get_uuid(log_id=None):
    """获取统一标识"""
    return log_id if log_id else uuid.uuid4().get_hex()


def data_truncation(data, data_limit_size=None):
    """序列化参数"""
    # 限制数据的大小
    return data[:data_limit_size] if data_limit_size and data else data


def get_search_params(params):
    """去掉为空的字段"""
    return {key: val for key, val in params.iteritems() if val}
