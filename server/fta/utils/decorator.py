# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import cPickle
import functools

from fta import constants
from fta.storage.cache import Cache
from fta.utils import logging, timeout

logger = logging.getLogger('utils')
redis_cache = Cache('redis')
instance_cache = Cache()


class try_exception(object):

    """
    decorator. log exception if task_definition has
    """

    def __init__(self, exception_desc=None, exception_return=None, log=True):
        self.exception_desc = exception_desc
        self.exception_return = exception_return
        self.is_log = log

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            try:
                return task_definition(*args, **kwargs)
            except timeout.TimeoutError:
                raise
            except Exception as e:
                desc = self.exception_desc or task_definition.func_name
                if self.is_log:
                    logger.exception(u"%s: %s", desc, e)
                else:
                    logger.warning(u"%s: %s", desc, e)
                return self.exception_return
        return wrapper


class redis_lock(object):

    """
    Distributed lock by redis
    """

    def __init__(self, key, timeout, redis_client=None):
        self.key = key
        self.timeout = timeout
        self.redis_client = redis_client or redis_cache

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            key = "--lock_%s--" % self.key
            value = "--lock--"
            if self.redis_client.set(
                    key, value, self.timeout, nx=True):
                return task_definition(*args, **kwargs)
            return False
        return wrapper


class CacheDecoratorBase(object):

    def __init__(self, timeout=None, backend=None,
                 ignore_argv=False, ignore_blank_result=True):
        """
        :param timeout: cache's timeout, default 1 day.
        :param backend: default redis+instance.
        """
        # cache expired time
        self.timeout = timeout or constants.CACHE_TIMEOUT
        self.backend = backend
        # ignore argv to get cache key or not
        self.ignore_argv = ignore_argv
        self.ignore_blank_result = ignore_blank_result
        self.func_name = "--defalut_func_name--"

    def get_cache_key(self, args, kwargs, prefix=""):
        if self.ignore_argv:
            cache_key = "func_cache.%s.%s" % (prefix, self.func_name)
        else:
            cache_key = "func_cache.%s.%s:%s,%s" % (
                prefix,
                self.func_name,
                cPickle.dumps(args),
                cPickle.dumps(kwargs))
        return cache_key

    def get_value_from_cache(self):
        return_value = None

        if not self.backend or self.backend == 'instance':
            return_value = instance_cache.get(self.cache_key)

            if return_value is not None:
                # logger.info("func_cache instance hit: %s", self.func_name)
                return return_value

        if not self.backend or self.backend == 'redis':
            return_value = redis_cache.get(self.cache_key)
            if return_value is not None:
                try:
                    return_value = cPickle.loads(return_value)
                    logger.info("func_cache redis hit: %s", self.func_name)
                    self.set_value_to_instance_cache(return_value)
                except Exception as e:
                    return_value = None
                    logger.error(
                        u"func_cache load from redis error: {}".format(e))

        return return_value

    def set_value_to_redis_cache(self, value):
        try:
            redis_cache.set(
                self.cache_key, cPickle.dumps(value), self.timeout)
        except Exception as e:
            logger.error(u"func_cache redis set error: {}".format(e))

    def set_value_to_instance_cache(self, value):
        try:
            instance_cache.set(
                self.cache_key, value, self.timeout)
        except Exception as e:
            logger.error(u"func_cache instance set error: {}".format(e))

    def set_value_to_cache(self, value):

        if not self.backend or self.backend == 'redis':
            self.set_value_to_redis_cache(value)

        if not self.backend or self.backend == 'instance':
            self.set_value_to_instance_cache(value)


class exception_cache(CacheDecoratorBase):

    """
        Get data from cache if task_definition raise exception
    """

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            self.func_name = task_definition.func_name
            self.cache_key = self.get_cache_key(args, kwargs, "ec")
            try:
                return_value = task_definition(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    u"exception_cache %s: %s",
                    task_definition.func_name, e)
                return_value = self.get_value_from_cache()
                if not return_value:
                    raise
            self.set_value_to_cache(return_value)
            return return_value
        return wrapper


class func_cache(CacheDecoratorBase):

    """
        Get data from cache if not expired.
        Used for avoiding high load balance
    """

    def __call__(self, task_definition):

        def raw(*args, **kwargs):
            return_value = task_definition(*args, **kwargs)
            self.set_value_to_cache(return_value)
            return return_value

        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            self.func_name = task_definition.func_name
            self.cache_key = self.get_cache_key(args, kwargs, "fc")
            return_value = self.get_value_from_cache()
            if return_value is not None:
                if not self.ignore_blank_result or return_value:
                    return return_value
            logger.info("func_cache miss: %s", self.func_name)
            return raw(*args, **kwargs)

        wrapper.raw = raw
        return wrapper
