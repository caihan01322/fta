# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import datetime

import arrow
import croniter

from fta import constants, settings
from fta.storage.queue import MessageQueue
from fta.utils import extended_json, get_random_id, logging

logger = logging.getLogger("scheduler")

SCHEDULER_QUEUE = MessageQueue('beanstalkd', settings.QUEUE_SCHEDULER)
POLLING_QUEUE = MessageQueue('beanstalkd', settings.QUEUE_POLLING)


def run(module, function, args=(), kwargs={}, cron="", time="", delta_seconds=0, timeout=None, id_=None):
    """
    create a scheduler job
    will call callback function in new process
    :param module: callback function's module name
    :param function: callback function's function name
    :param args: callback function's args
    :param kwargs: callback function's kwargs
    :param cron: cron descripton like "* * * * *"
    :param time: the specified exec time
    :param delta_seconds: delay seconds
    :param timeout: timeout of exec callback function
    :param id_: poll job's id, default will create by random
    mush have "time" or "delta_seconds" or "cron"
    """
    delta_seconds, task_info = get_task_info(**locals())
    logger.info("scheduler delay %s: %s", delta_seconds, task_info)
    SCHEDULER_QUEUE.put(task_info, delay=delta_seconds)


def poll(module, function, args=(), kwargs={}, cron="", time="", delta_seconds=0, timeout=None, id_=None):
    """
    create a poll job
    will polling a url then use result as kwargs to call callback function
    :param module: callback function's module name
    :param function: callback function's function name
    :param args: callback function's args
    :param kwargs: **kwargs for requests.post,
                   callback will be {"result": r.json()}
                   (r = requests.post(**kwargs))
    :param cron: cron descripton like "* * * * *"
    :param time: the specified exec time
    :param delta_seconds: delay seconds
    :param timeout: timeout of polling request
    :param id_: poll job's id, default will create by random
    mush have "time" or "delta_seconds" or "cron"
    """
    delta_seconds, task_info = get_task_info(**locals())
    logger.info("polling delay %s: %s", delta_seconds, task_info)
    POLLING_QUEUE.put(task_info, delay=delta_seconds)


def get_task_info(module, function, args=(), kwargs={}, cron="", time="", delta_seconds=0, timeout=None, id_=None):
    assert time or cron or delta_seconds

    if delta_seconds:
        time = time or get_time_by_delta(delta_seconds)
    elif cron:
        time = time or get_time_by_cron(cron)

    delta_seconds = delta_seconds or get_delta_seconds(time)

    task_info = extended_json.dumps({
        "id": id_ or get_random_id(),
        "module": module,
        "function": function,
        "args": args,
        "kwargs": kwargs,
        "cron": cron,
        "time": time,
        "timeout": timeout
    })
    return delta_seconds, task_info


def get_time_by_delta(delta_seconds):
    return arrow.utcnow().replace(seconds=delta_seconds).format(constants.STD_ARROW_FORMAT)


def get_time_by_cron(cron):
    return croniter.croniter(cron, arrow.utcnow().naive).get_next(
        ret_type=datetime.datetime).strftime(constants.STD_DT_FORMAT)


def get_delta_seconds(time):
    exec_time = arrow.get(time).replace(tzinfo="utc")
    return max(0, (exec_time - arrow.utcnow()).total_seconds())
