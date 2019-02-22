# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import random
import sys

import arrow

from fta.converge import CONTEXT
from fta.storage.cache import Cache, RedisIndexException
from fta.utils import logging

logger = logging.getLogger('converge')
redis = Cache("dimension")


class DimensionHandler(object):

    def __init__(self, dimension, condition, start_timestamp):
        """
        :param dimension: the result key for redis
        :param condition: dict {"dimension_key": ["dimension_value", ]}
        :param start_timestamp: start time's timestamp
        """
        self._redis_conf_len = len(redis.redis_conf)
        self.redis_index = random.randint(0, self._redis_conf_len - 1)
        self.dimension = dimension
        self.condition = condition
        self.start_timestamp = start_timestamp
        logger.info("$%s condition %s", CONTEXT.get("id"), json.dumps(self.condition))

    def get_by_condition(self):
        """
        :return event_id_list: alarm's(matched condition) event_id_list
        """
        for index_delta in range(self._redis_conf_len):
            # _call_index_redis_method默认是没有failover的，需要在这里做failover
            try:
                return self._get_by_condition((self.redis_index + index_delta) % self._redis_conf_len)
            except RedisIndexException:
                pass
        raise Exception("$%s get_by_condition all failure" % CONTEXT.get("id"))

    def _get_by_condition(self, redis_index=None):
        redis_index = redis_index or self.redis_index

        redis_key_list = [self.get_key_by_kv(key, values, redis_index) for key, values in self.condition.items()]
        redis.set_index(redis_index).zinterstore(
            dest=self.dimension, keys=redis_key_list, aggregate="MIN")
        result_list = redis.set_index(redis_index).zrangebyscore(
            self.dimension,
            self.start_timestamp,
            arrow.utcnow().timestamp,
            withscores=True)
        logger.info(
            "$%s dimension_key %s (%s) ten:%s filter:%s-%s",
            CONTEXT.get("id"),
            self.dimension,
            redis.set_index(redis_index).zcard(self.dimension),
            redis.set_index(redis_index).zrange(self.dimension, 0, 10, withscores=True),
            self.start_timestamp, arrow.utcnow().timestamp)
        redis.lpush('zset_key_list', self.dimension)
        return [m[0] for m in result_list]

    def get_key_by_kv(self, key, values, redis_index=None):
        """
        :param key: condition's dimension_key
        :param values: condition's dimension_value_list
        :param redis_index: condition's redis_index
        :return redis_index: redis_index's value is event_id_list
        """

        redis_index = redis_index or self.redis_index

        # get value list from values
        value_list = []
        for value in values:
            if not isinstance(value, list):
                value = [str(value)]
            value_list.extend(value)

        # make result redis_key
        redis_key = "%s_%s" % (key, ','.join(value_list))

        # get all set_key
        set_keys = ["%s_%s" % (key, v) for v in value_list] if value_list else ["%s_" % key]

        # union set_keys to redis_key by redis
        redis.set_index(redis_index).zunionstore(dest=redis_key, keys=set_keys, aggregate="MIN")
        redis.lpush('zset_key_list', redis_key)

        logger.info(
            "$%s dimension_key %s (%s)",
            CONTEXT.get("id"), redis_key,
            redis.set_index(redis_index).zcard(redis_key))
        return redis_key

    @staticmethod
    def clean_key():
        """clear 2 days ago's dimension info"""
        start = arrow.utcnow().replace(years=-2).timestamp
        end = arrow.utcnow().replace(days=-2).timestamp
        zset_key_list = set()
        while True:
            key = redis.lpop('zset_key_list')
            if not key:
                break
            redis.zremrangebyscore(key, start, end)
            if redis.zcard(key):
                zset_key_list.add(key)
        if zset_key_list:
            redis.lpush('zset_key_list', *list(zset_key_list))


if __name__ == "__main__":
    if sys.argv[1] == 'clean':
        DimensionHandler.clean_key()
