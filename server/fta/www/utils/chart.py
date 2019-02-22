# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow

from fta import constants
from fta.storage.cache import Cache
from fta.utils import logging

redis = Cache("redis")

logger = logging.getLogger("webserver")


class Data(object):

    KEY_PREFIX = "fta_chart"

    @staticmethod
    def get_key(key):
        return "%s_%s" % (Data.KEY_PREFIX, key)

    @staticmethod
    def format(timestamp):
        return arrow.get(timestamp).to("local")\
            .format(constants.MINI_ARROW_FORMAT)

    @staticmethod
    def add_point(key, time, value, replace_tz=False):
        Data.clean_key(key)
        time = arrow.get(time).floor("minute")
        if replace_tz:
            time = time.replace(tzinfo="local")
        redis.zremrangebyscore(
            Data.get_key(key), time.timestamp, time.timestamp)
        redis.zadd(Data.get_key(key), **{str(value): time.timestamp})
        logger.info("CHART %s %s %s", key, Data.format(time.timestamp), value)

    @staticmethod
    def get_list(key, begin=60 * 60 * 24, end=0, interval=60):
        Data.clean_key(key)
        begin = arrow.utcnow().replace(seconds=-1 * int(begin))\
            .floor("minute").timestamp
        end = arrow.utcnow().replace(seconds=-1 * int(end))\
            .floor("minute").timestamp
        result = redis.zrangebyscore(
            Data.get_key(key), begin, end, withscores=True)
        key_list = []
        value_list = []
        for value, key in result:
            while int(key) > begin:
                key_list.append(Data.format(begin))
                value_list.append(0)
                begin += int(interval)
            if len(key_list) and key_list[-1] == Data.format(begin):
                value_list[-1] = max(int(value), value_list[-1])
            else:
                key_list.append(Data.format(begin))
                value_list.append(int(value))
            begin = int(key) + int(interval)
        return key_list, value_list

    @staticmethod
    def clean_key(key):
        begin = arrow.utcnow().replace(years=-2).timestamp
        end = arrow.utcnow().replace(days=-2).timestamp
        redis.zremrangebyscore(Data.get_key(key), begin, end)
