# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import gevent
from gevent import monkey

from fta.utils import logging

monkey.patch_socket()

logger = logging.getLogger("polling")


def wrapper(func, kwargs):
    index = kwargs.pop("index")
    result = kwargs.pop("result")
    logger.info("scheduler poll begin(%s) %s %s", index, func.__name__, kwargs)
    result[index] = func(**kwargs)
    logger.info("scheduler poll end(%s) %s %s", index, func.__name__, kwargs)


def parallel(func, kwargs_list):
    result = [None] * len(kwargs_list)
    for index, kwargs in enumerate(kwargs_list):
        kwargs["index"] = index
        kwargs["result"] = result
    threads = [gevent.spawn(wrapper, func, kwargs) for kwargs in kwargs_list]
    gevent.joinall(threads)
    return result
