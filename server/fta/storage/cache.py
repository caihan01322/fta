# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools
import sys
import time

import redis

from fta import constants, settings
from fta.utils import get_list, logging

logger = logging.getLogger('root')


class RedisIndexException(Exception):
    pass


class InstanceCache(object):

    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.__cache = {}

    def clear(self):
        self.__cache = {}

    def set(self, key, value, seconds=0):
        self.__cache[key] = (value, time.time() + seconds if seconds else 0)

    def get(self, key):
        value = self.__cache.get(key)
        if not value:
            return None
        if value[1] and time.time() > value[1]:
            del self.__cache[key]
            return None
        return value[0]

    def delete(self, key):
        try:
            del self.__cache[key]
        except BaseException:
            pass


class CacheBackendMixin(object):
    BACKEND_CONF = {
        "redis": settings.REDIS_CACHE_CONF,
        "dimension": settings.REDIS_DIMENSION_CONF,
        "callback": settings.REDIS_CALLBACK_CONF,
        "localcache": settings.REDIS_LOCALCACHE_CONF,
        "log": settings.REDIS_LOG_CONF,
        "test": settings.REDIS_TEST_CONF,
    }

    @classmethod
    def instance(cls, backend):
        _instance = "_%s_instance" % backend
        if not hasattr(cls, _instance):
            if backend not in cls.BACKEND_CONF:
                raise Exception("unknow redis backend %s" % backend)
            ins = cls(cls.BACKEND_CONF[backend])
            setattr(cls, _instance, ins)
        return getattr(cls, _instance)


class RedisCache(CacheBackendMixin):
    DEFAULT_RESULT = '--default_result--'

    def __init__(self, redis_conf):
        self.index = None
        self.redis_conf = get_list(redis_conf)
        self.redis_host = [conf['host'] for conf in self.redis_conf]
        self.redis = self._connect(True)

    def _connect(self, soft=False):
        self._reconnect = 0
        redis_list = []
        for cache_conf in self.redis_conf:
            try:
                cache_conf["socket_timeout"] = cache_conf.get(
                    "socket_timeout", 5)
                r = redis.StrictRedis(**cache_conf)
                r.set('--test_key--', '--test_data--', 10)
                r.get('--test_key--')
            except Exception as e:
                logger.info("redis connect error: %s", e)
                self._reconnect = time.time() + settings.RECONNECT_INTERVAL
                redis_list.append(None)
            else:
                redis_list.append(r)
        if not soft and not len([r_ for r_ in redis_list if r_ is not None]):
            raise Exception("redis all dead: %s" % ','.join(self.redis_host))
        return redis_list

    def _call_redis_method(self, method, *args, **kwargs):
        result = self.DEFAULT_RESULT
        # last_result = self.DEFAULT_RESULT
        for index, r in enumerate(self.redis):
            try:
                result = self._call_index_redis_method(
                    method, index, *args, **kwargs)
            except RedisIndexException:
                pass
        if result == self.DEFAULT_RESULT:
            raise Exception("redis all dead: %s" % ','.join(self.redis_host))
        return result

    def _call_index_redis_method(self, method, index, *args, **kwargs):
        """Only use a given redis.
            If connect error, do not failover here. Just raise an exception,
            and let the caller retry if necessary.
        """
        _redis = self.redis[index]
        try:
            result = getattr(_redis, method)(*args, **kwargs)
        except Exception as e:
            self._reconnect = self._reconnect or \
                time.time() + settings.RECONNECT_INTERVAL
            logger.info("redis error (%s) %s: %s(*%.30s, **%.30s)",
                        self.redis_host[index], e, method, args, kwargs)
            raise RedisIndexException(
                "redis connect error for index %d" % index)
        return result

    def __getattr__(self, method):
        if self._reconnect and self._reconnect <= time.time():
            logger.info("Try to reconnect redis")
            self.redis = self._connect()
        if self.index is not None:
            # self.index should be None before call _call_index_redis_method
            tmp_index, self.index = self.index, None
            return functools.partial(
                self._call_index_redis_method, method, tmp_index)
        return functools.partial(self._call_redis_method, method)

    def set_index(self, index):
        """use a given index
            Example:
                r.set_index(2).zinterstore(foo, bar)
        """
        assert index < len(self.redis_conf)
        self.index = index
        return self


class SentinelRedisCahce(CacheBackendMixin):
    SOCKET_TIMEOUT = getattr(settings, "REDIS_SOCKET_TIMEOUT", 0.1)
    MASTER_NAME = getattr(settings, "REDIS_MASTER_NAME", "mymaster")

    def __init__(self, conf):
        from redis.sentinel import Sentinel

        sentinel_conf = []
        redis_conf = {}

        for i in conf:
            sentinel_conf.append((i.pop("host"), i.pop("port")))
            redis_conf.update(i)

        socket_timeout = redis_conf.pop("socket_timeout", self.SOCKET_TIMEOUT)
        self.master_name = redis_conf.pop("master_name", self.MASTER_NAME)
        self.cache_mode = redis_conf.pop("cache_mode", "master")
        self.conf = redis_conf
        self.sentinel_conf = sentinel_conf
        self.redis_sentinel = Sentinel(sentinel_conf, socket_timeout)
        if self.cache_mode == "master":
            self.instance = self.get_master()
        else:
            self.instance = self.get_slave()

    @property
    def redis_conf(self):
        return [self.conf]

    @property
    def index(self):
        if self.cache_mode == "master":
            return 0
        else:
            return 1

    def set_index(self, *args, **kwargs):
        logger.warning("do not set index for SentinelRedisCahce")
        return self

    def get_master(self):
        return self.redis_sentinel.master_for(
            self.master_name, **self.conf
        )

    def get_slave(self):
        return self.redis_sentinel.slave_for(
            self.master_name, **self.conf
        )

    def __getattr__(self, name):
        return getattr(self.instance, name)


class Cache(object):
    CacheTypes = {
        "SentinelRedisCahce": SentinelRedisCahce,
        "RedisCache": RedisCache,
        "InstanceCache": InstanceCache,
    }
    CacheBackendType = getattr(settings, "CACHE_BACKEND_TYPE", "RedisCache")
    CacheDefaultType = getattr(settings, "CACHE_DEFAULT_TYPE", "InstanceCache")

    def __new__(cls, backend=None):
        try:
            if backend:
                type_ = cls.CacheTypes[cls.CacheBackendType]
                return type_.instance(backend)
        except Exception:
            logger.exception(
                "%s fail to use %s [%s]", constants.ERROR_03_REDIS, backend, ' '.join(sys.argv))
            raise
        type_ = cls.CacheTypes[cls.CacheDefaultType]
        return type_.instance()
