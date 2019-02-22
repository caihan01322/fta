# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
"""性能监控器
"""
import time

from fta.utils import logging

logger = logging.getLogger(__name__)


class Performance(object):
    def __init__(self, obj):
        self.obj = obj
        self.size = 0
        self.count = 0
        self.st = time.time()

    def incr_size(self, size):
        self.size += size

    def incr_count(self, count):
        self.count += count

    def report(self, type='LOG'):
        logger.info('%s Performance report BEGIN', self.obj)

        duration = time.time() - self.st
        logger.info('%s duration: %.3f', self.obj, duration)

        count_perf = self.count / duration
        logger.info('%s count: %s %s', self.obj, self.count)
        logger.info('%s result: %.3f/s, %.3f/m, %.3f/h',
                    self.obj, count_perf, count_perf * 60, count_perf * 3600)

        size = self.size / 1024.0 / 1024.0
        size_perf = size / duration
        logger.info('%s size: %.3f(Mb)', self.obj, size)
        logger.info('%s result: %.3f(Mb)/s, %.3f(Mb)/m, %.3f(Mb)/h',
                    self.obj, size_perf, size_perf * 60, size_perf * 3600)

        logger.info('%s Performance report END', self.obj)
