# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import importlib
import json
import re

from fta_utils.cache import CACHE_KEY_LIST_KEY
from fta_utils.cache import cache
from fta_utils.cache import del_cache_key
from fta_utils.cache import logger
from fta_utils.cache import web_cache

CACHE_FUNC_MODULE = "fta_solutions_app.cache_utils"


def update_cache(force_run=False):
    """缓存更新函数，由定时任务调用执行"""
    cache_key_list = cache.get(CACHE_KEY_LIST_KEY, [])
    logger.info('CACHE START update_cache: %s' % cache_key_list)
    r = re.compile("""cache.(\w+):(\[.*\]),(\{.*\})""")

    for cache_key in cache_key_list:

        # 读取出缓存 KEY，解析参数
        try:
            func_name, args, kwargs = r.findall(cache_key)[0]
            args = json.loads(args)
            kwargs = json.loads(kwargs)
        except Exception as e:
            logger.error("CACHE key(%s) parse error: %s" % (cache_key, e))
            del_cache_key(cache_key)
            continue

        # 加载真实函数
        try:
            cache_func_module = importlib.import_module(CACHE_FUNC_MODULE)
            func = getattr(cache_func_module, func_name)
        except Exception, e:
            del_cache_key(cache_key)
            continue
            logger.error("CACHE func(%s) import error: %s" % (func_name, e))

        # 执行真实函数
        try:
            if force_run is True:
                web_cache(auto_refresh=True)._call(func, args, kwargs)
            else:
                func(*args, **kwargs)
        except Exception, e:
            del_cache_key(cache_key)
            logger.error("CACHE func(%s) run error: %s" % (func_name, e))

    logger.info('CACHE END')
