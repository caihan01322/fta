# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools
import json
import time

from django.core.cache import cache

from common.log import logger

CACHE_KEY_LIST_KEY = "cache_key_list"
CACHE_KEY_LIST_TIMEOUT = 60 * 60 * 24 * 3


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
        except Exception:
            pass


instance_cache = InstanceCache()


class web_cache(object):

    def __init__(self, time_out=60 * 60 * 24, auto_refresh=False):
        self.time_out = time_out
        # 是否自动刷新缓存
        # 需要有定时任务支持
        # 可以保证缓存在没有人使用情况下也自动更新
        # 但注意不要将太多的缓存加到自动更新队列
        # 注意：auto_refresh目前只支持cache_utils模块中的函数
        # 其他模块里的请不要使用
        self.auto_refresh = auto_refresh

    def _cache_key(self, func_name, args, kwargs):
        return 'cache.%s:%s,%s' % (
            func_name,
            json.dumps(args),
            json.dumps(kwargs))

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):

            cache_key = self._cache_key(task_definition.func_name, args, kwargs)

            # 从内存读取缓存
            return_value = instance_cache.get(cache_key)
            if return_value is None:
                logger.info("Cache miss ins: %s" % cache_key)
            else:
                return return_value

            # 从DB读取缓存
            return_value = cache.get(cache_key)
            if return_value is None:
                return_value = self._call(task_definition, args, kwargs)
                logger.info("Cache miss: %s" % cache_key)
            else:
                logger.info("Cache hit: %s" % cache_key)

            instance_cache.set(cache_key, return_value, self.time_out)
            return return_value

        return wrapper

    def _call(self, task_definition, args, kwargs):

        cache_key = self._cache_key(task_definition.func_name, args, kwargs)

        logger.info(u"Cache CALL %s" % cache_key)

        # 执行真实函数
        return_value = task_definition(*args, **kwargs)

        # 记录缓存
        try:
            cache.set(cache_key, return_value, self.time_out)
        except Exception, e:
            # 缓存出错不影响主流程
            logger.error(u"存缓存时报错：{}".format(e))

        # 如果自动刷新，添加到刷新列表里
        if self.auto_refresh:
            add_cache_key(cache_key)

        return return_value


def add_cache_key(cache_key):
    """每次请求缓存时，在定时更新列表里注册"""
    logger.info("Cache add_key: %s" % cache_key)
    cache_key_list = cache.get(CACHE_KEY_LIST_KEY, [])
    if cache_key not in cache_key_list:
        cache_key_list.append(cache_key)
        cache_key_list = list(set(cache_key_list))
        cache.set(CACHE_KEY_LIST_KEY, cache_key_list, CACHE_KEY_LIST_TIMEOUT)


def del_cache_key(cache_key):
    """更新缓存时，删除 key。在函数执行成功后会被重新加上"""
    logger.info("Cache del_key: %s" % cache_key)
    cache_key_list = cache.get(CACHE_KEY_LIST_KEY, [])
    if cache_key in cache_key_list:
        cache_key_list.remove(cache_key)
        cache.set(CACHE_KEY_LIST_KEY, cache_key_list, CACHE_KEY_LIST_TIMEOUT)
