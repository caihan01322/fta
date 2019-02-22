# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import Queue
import random
import sys
import time

import beanstalkc
import kafka
from fta import constants, settings
from fta.utils import get_list, logging

logger = logging.getLogger('root')


class BaseQueue(object):

    def __init__(self, topic=None):
        pass

    def put(self, value, priority=1):
        pass

    def take(self, count=1, timeout=settings.QUEUE_WAIT_TIMEOUT):
        pass


class InstanceQueue(BaseQueue):

    @classmethod
    def queue_dict(cls):
        if not hasattr(cls, '_queue_dict'):
            cls._queue_dict = {}
        return cls._queue_dict

    def __init__(self, topic=None):
        topic = topic or 'DEFAULT'
        queue_dict = InstanceQueue.queue_dict()
        self.queue = queue_dict.get(topic, Queue.Queue())

    def put(self, value, priority=1):
        return self.queue.put(value)

    def take(self, count=1, timeout=settings.QUEUE_WAIT_TIMEOUT):
        try:
            return self.queue.get(timeout=timeout)
        except Queue.Empty:
            return []

    def total_jobs_ready(self):
        queue_dict = InstanceQueue.queue_dict()
        return len(queue_dict)


class BeanstalkdQueue(BaseQueue):

    @classmethod
    def instance(cls, topic=None, host=None, port=None):
        _instance = "_%s_instance" % topic
        if not hasattr(cls, _instance):
            setattr(cls, _instance, cls(topic, host, port))
        return getattr(cls, _instance)

    def __init__(self, topic=None, host=None, port=None):
        self.topic = topic
        self.host = host or get_list(settings.BEANSTALKD_HOST)
        self.port = port or settings.BEANSTALKD_PORT
        self.beans = self._connect(True)

    def _connect(self, soft=False):
        beans = []
        self._reconnect = 0
        for host in self.host:
            try:
                bean = beanstalkc.Connection(
                    host=host, port=self.port, connect_timeout=8)
            except Exception as e:
                logger.exception("%s beanstalk error: %s", constants.ERROR_03_BEANSTALK, e)
                self._reconnect = time.time() + settings.RECONNECT_INTERVAL
                continue
            if self.topic:
                bean.use(self.topic)
                bean.watch(self.topic)
            beans.append(bean)
        if len(beans) > 1:
            self.index = random.randint(0, len(beans) - 1)
        elif beans:
            self.index = 0
        elif not soft:
            raise Exception("beanstalk all dead")
        return beans

    def put(self, value, priority=1, **kwargs):
        if self._reconnect and self._reconnect <= time.time():
            logger.info("Try to reconnect beanstalkd")
            self.beans = self._connect()
        if "ttr" not in kwargs:
            kwargs["ttr"] = 24 * 60 * 60
        error = True
        for beans in self.beans:
            try:
                beans.put(value, priority, **kwargs)
            except Exception as e:
                self._reconnect = self._reconnect or time.time() + settings.RECONNECT_INTERVAL
                logger.error(
                    "%s beanstalk error in put: %s, %s, %s",
                    constants.ERROR_03_BEANSTALK, value, priority, e)
                continue
            error = False
        if error:
            raise Exception("beanstalk all dead")

    def take(self, count=1, timeout=None, **kwargs):
        if self._reconnect and self._reconnect <= time.time():
            logger.info("Try to reconnect beanstalkd")
            self.beans = self._connect()
        beans = self.beans[self.index]
        try:
            self.index = (self.index + 1) % len(self.beans)
            return beans.reserve(timeout=timeout, **kwargs)
        except Exception as e:
            self._reconnect = self._reconnect or time.time() + settings.RECONNECT_INTERVAL
            logger.exception("%s beanstalk error in take: %s", constants.ERROR_03_BEANSTALK, e)
            return None

    def total_jobs_ready(self):
        if self._reconnect and self._reconnect <= time.time():
            logger.info("Try to reconnect beanstalkd")
            self.beans = self._connect()
        error = True
        jobs_ready_len = 0
        for bean in self.beans:
            try:
                if self.topic:
                    jobs_ready_len += bean.stats_tube(self.topic)[
                        'current-jobs-ready']
                else:
                    jobs_ready_len += bean.stats()[
                        'current-jobs-ready']
            except Exception as e:
                self._reconnect = self._reconnect or time.time() + settings.RECONNECT_INTERVAL
                logger.error("%s beanstalk error in total_jobs_ready: %s", constants.ERROR_03_BEANSTALK, e)
                continue
            error = False
        if error:
            raise Exception("beanstalk all dead")
        return jobs_ready_len


class MessageQueue(object):

    def __new__(cls, backend=None, topic=None, *args, **kwargs):
        try:
            if backend == 'beanstalkd':
                return BeanstalkdQueue.instance(topic, *args, **kwargs)
        except Exception:
            logger.exception(
                "fail to use %s [%s]", backend, ' '.join(sys.argv))
        return InstanceQueue(topic)
