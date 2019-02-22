# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import importlib

from fta.utils import logging
from fta.utils.timeout import TimeoutError, set_timeout

logger = logging.getLogger('scheduler')


def call_task(module_name, function_name, args, kwargs):
    """
    import && call real function
    :param module: function's module's name or path
    :param function_name: function's name which is to be exec
    :param args: args' list
    :param kwargs: kwargs' dict
    """
    logger.info('scheduler BEGIN: %s.%s', module_name, function_name)
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    function(*args, **kwargs)
    logger.info('scheduler END: %s.%s', module_name, function_name)


def run(module, function, timeout=None, args=(), kwargs={}):
    """
    run job with try/exception && timeout limit
    :param module: function's module's name or path
    :param function: function's name which is to be exec
    :param timeout: seconds or not
    :param args: args' list
    :param kwargs: kwargs' dict
    """
    try:
        if timeout is not None:
            set_timeout(int(timeout))
        call_task(module, function, args, kwargs)
    except TimeoutError as e:
        logger.error(u'SCHEDULER TASK TIMEOUT: %s', function)
    except Exception as e:
        logger.exception(u'SCHEDULER TASK ERROR: %s', e)
