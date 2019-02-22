# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

"""count function's running time"""

import functools
import time

from fta.utils import logging

logger = logging.getLogger("utils")


def timer(func):
    """count function's running time, record a log"""
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        beg_ts = time.time()
        exec_res = func(*args, **kwargs)
        end_ts = time.time()
        cost_ts = end_ts - beg_ts
        logger.info("%s costs time %s(s)" % (func.__name__, cost_ts))
        return exec_res
    return _wrapper


def time_limiter(seconds, desc=None):
    """count function's running time, send error if beyond the limit"""
    def limiter(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            beg_ts = time.time()
            exec_res = func(*args, **kwargs)
            end_ts = time.time()
            cost_ts = end_ts - beg_ts
            if cost_ts > seconds:
                logger.error(u"%s costs %s(s), time_limit(%s)" % (
                    desc or func.__name__, cost_ts, seconds))
            else:
                logger.info("%s costs %s(s)" % (func.__name__, cost_ts))
            return exec_res
        return _wrapper
    return limiter
