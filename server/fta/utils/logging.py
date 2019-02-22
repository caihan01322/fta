# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from __future__ import absolute_import

import logging
import logging.config
from contextlib import contextmanager

from fta import settings

logging.config.dictConfig(settings.LOGGER_CONF)

NOTSET, DEBUG, INFO, WARNING, ERROR, EXCEPTION, CRITICAL = \
    0, 10, 20, 30, 40, 40, 50


def getLogger(name):
    return logging.getLogger(name)


@contextmanager
def logger_disable(name, level=logging.WARNING):
    logger = getLogger(name)
    logger_level = logger.level
    logger.setLevel(level)
    try:
        yield logger_level
    finally:
        logger.setLevel(logger_level)
