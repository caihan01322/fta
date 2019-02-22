# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import inspect

import arrow

from fta.storage.cache import Cache
from fta.utils import get_random_id, logging, scheduler

redis_cache = Cache("redis")

logger = logging.getLogger("utils")


class SliceWindow(object):

    def __init__(self, key_prefix="",
                 time=60 * 30, count=15, slice_time=60 * 10, slice_count=10):
        self.key_prefix = key_prefix
        self.time, self.count = time, count
        self.slice_time, self.slice_count = slice_time, slice_count

    def check_defense(self, key):
        notify_ts = arrow.utcnow().timestamp
        self.incr_defense_key(key, notify_ts)
        values = map(int, [
            redis_cache.get(self.get_notify_key(key, bucket)) or 0
            for bucket in self.get_buckets(notify_ts)])
        logger.info("SliceWindow %s %s: %s", self.key_prefix, key, values)
        return sum(values) > self.count or values[-1] > self.slice_count

    def incr_defense_key(self, key, notify_ts):
        notify_bucket = self.get_bucket(notify_ts)
        notify_key = self.get_notify_key(key, notify_bucket)
        logger.debug("SliceWindow incr key %s", notify_key)
        redis_cache.expire(notify_key, self.slice_time + self.time)
        redis_cache.incr(notify_key)
        redis_cache.expire(notify_key, self.slice_time + self.time)

    def get_notify_key(self, key, notify_bucket):
        return "%s-%s-%s" % (self.key_prefix, key, notify_bucket)

    def get_bucket(self, notify_ts):
        return notify_ts - notify_ts % self.slice_time

    def get_buckets(self, notify_ts):
        return [self.get_bucket(notify_ts - self.slice_time * i)
                for i in range(self.time / self.slice_time)]


class SlidingWindow(object):

    def __init__(self, key, time_range, count=None, redis_client=redis_cache):
        self.key = key
        self.time_range = time_range
        self.count = count
        self.redis_client = redis_client

    def acquire(self, value=None):
        value = str(value or get_random_id())
        scope = arrow.utcnow().timestamp
        notify_list = self.get_list(scope)
        if self.count and len(notify_list) < self.count:
            self.redis_client.zadd(self.key, **{value: scope})
            self._del_expire()
            return False, notify_list
        else:
            return True, notify_list

    def get_list(self, scope):
        return self.redis_client.zrangebyscore(
            self.key,
            scope - self.time_range,
            scope,
            withscores=True)

    def clear(self):
        return self.redis_client.delete(self.key)

    def _del_expire(self):
        self.redis_client.zremrangebyscore(
            self.key,
            arrow.utcnow().replace(years=-1).timestamp,
            arrow.utcnow().replace(days=-1).timestamp)


def check_defense(callback_func, callback_kwargs, time, count,
                  obj_id, key_prefix="CK_DEF", key_args=[]):
    frm = inspect.stack()[1]
    callback_module = inspect.getmodule(frm[0]).__name__

    defense_key = "%s_%s" % (key_prefix, "-".join(map(str, key_args)))

    slideing_window = SlidingWindow(defense_key, time, count)
    should_defense, notify_list = slideing_window.acquire(obj_id)
    logger.info("$%s %s list %s", obj_id, key_prefix, len(notify_list))

    if key_args:
        key_args.insert(0, defense_key)
        args = key_args
    else:
        args = [defense_key]

    if should_defense:
        delta_seconds = time - (arrow.utcnow().timestamp - notify_list[0][1])
        scheduler.run(
            module=callback_module,
            function=callback_func.func_name,
            args=args,
            kwargs=callback_kwargs,
            delta_seconds=max(delta_seconds, 1),
            id_=notify_list[0][0])
        return True
    return False
