# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import functools
import signal

import arrow

from fta import settings
from fta.utils import extended_json


class TimeoutError(Exception):
    pass


def handler(signum, frame):
    raise TimeoutError("Time Out")


def set_timeout(seconds=None):
    seconds = int(seconds)
    if seconds <= 0:
        raise TimeoutError("Time Out")
    signal.signal(signal.SIGALRM, handler)
    return signal.alarm(seconds)


def del_timeout():
    signal.alarm(0)


def get_timeout_time(alarm_instance):
    alarm_def = extended_json.loads(alarm_instance['snap_alarm_def'])
    # if is retrying, won't timeout
    if alarm_instance["status"] == "retrying":
        return int(alarm_def['timeout']) * 60
    alarm_time = arrow.get(alarm_instance['source_time']).replace(tzinfo="utc")
    timeout_time = alarm_time.replace(minutes=int(alarm_def['timeout']))
    delta_seconds = (timeout_time - arrow.utcnow()).total_seconds()
    return int(delta_seconds)


class func_timeout(object):

    def __init__(self, timeout=settings.QUEUE_WAIT_TIMEOUT):
        self.timeout = timeout

    def __call__(self, task_definition):
        @functools.wraps(task_definition)
        def wrapper(*args, **kwargs):
            last_time = set_timeout(self.timeout)
            try:
                result = task_definition(*args, **kwargs)
            except TimeoutError:
                raise Exception("Time Out")
            finally:
                signal.alarm(last_time)
            return result
        return wrapper
