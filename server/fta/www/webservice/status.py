# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import json

import arrow

import beanstalkc
from flask import request
from fta import constants, settings
from fta.storage import tables
from fta.storage.cache import Cache
from fta.storage.mysql import session
from fta.utils import logging
from fta.utils.supervisorctl import get_supervisor_client
from fta.www.utils import response
from fta.www.webservice import fta_simple_page as app

logger = logging.getLogger("webserver")

redis = Cache('redis')

CHECK_PROCESS_KEY = "--check_precess--"


@app.route("/status/process/", methods=["GET"])
@response.log
def check_process():
    key = request.args.get('key', 'name')
    value = request.args.get('value', 'statename')
    return _check_process(key, value)


def _check_process(key='name', value='statename'):
    """查询supervisor的进程状态"""
    proxy = get_supervisor_client()
    status_dict = {
        prey[key]: prey[value]
        for prey in proxy.supervisor.getAllProcessInfo()}
    logger.info("check process %s", status_dict)
    redis.set(CHECK_PROCESS_KEY, constants.MARK_VALUE, 5 * 60)
    return json.dumps(status_dict)


@app.route("/status/beanstalk/", methods=["GET"])
@response.log
def check_bean_tubes():
    bean_queues = [
        settings.QUEUE_COLLECT,
        settings.QUEUE_CONVERGE,
        settings.QUEUE_SOLUTION,
        settings.QUEUE_JOB,
        settings.QUEUE_SCHEDULER,
        settings.QUEUE_POLLING,
        settings.QUEUE_MATCH
    ]

    stats = {}

    if isinstance(settings.BEANSTALKD_HOST, (list, set)):
        bean_hosts = settings.BEANSTALKD_HOST
    else:
        bean_hosts = [settings.BEANSTALKD_HOST]

    for host in bean_hosts:
        bean_stats = _get_bean_stats(host, settings.BEANSTALKD_PORT, bean_queues)
        key = '{host}:{port}'.format(**{'host': host, 'port': settings.BEANSTALKD_PORT})
        stats[key] = bean_stats

    return json.dumps(stats)


def _get_bean_stats(host, port, queues):
    """获取beanstalkd队列信息
    """
    bean = beanstalkc.Connection(host=host, port=port)

    bean_stats = {}
    try:
        main_stats = bean.stats()
    except Exception as e:
        logger.exception(e)
        main_stats = {"exception": str(e)}
    bean_stats['main'] = main_stats

    for q in queues:
        try:
            q_stats = bean.stats_tube(q)
        except Exception as e:
            logger.warning(e)
            q_stats = {"exception": str(e)}
        bean_stats[q] = q_stats
    return bean_stats


@app.route("/status/gaze/", methods=["GET", "POST"])
@response.log
def gaze():
    return "gaze"


@app.route("/status/archive/")
@response.log
def alarm_instance_archive():
    end_time = arrow.get(request.values.get("end_time"))
    start_time = end_time.replace(
        days=-int(request.values.get("date_delta", 1)),
    )

    result = {}
    for i in session.query(tables.FtaSolutionsAppAlarminstancearchive).filter(
        tables.FtaSolutionsAppAlarminstancearchive.date >= start_time,
        tables.FtaSolutionsAppAlarminstancearchive.date < end_time,
    ):
        key_dict = {
            "date": i.date.strftime("%Y-%m-%d %H:%M"),
            "failure_type": i.failure_type,
            "is_success": i.is_success,
            "source_type": i.source_type,
            "solution_type": i.solution_type,
            "alarm_type": i.alarm_type,
        }
        key = tuple(key_dict.values())
        info = result.get(key)
        if info is None:
            result[key] = info = {
                "sub_count": 0,
                "sub_consumed": 0,
                "sub_profit": 0,
            }
            info.update(key_dict)

        info["sub_count"] += i.sub_count
        info["sub_consumed"] += i.sub_consumed
        info["sub_profit"] += i.sub_profit

    return json.dumps(list(result.values()))


@app.route("/status/solution/")
@response.log
def solution_status():
    result = {
        "solution_monitor_success": 0,
        "solution_monitor_failure": 0,
    }
    result.update({
        "solution_monitor_failure:%s" % k: 0
        for k, d in constants.FAILURE_TYPE_CHOICES
    })
    for key in redis.keys("solution_monitor_*"):
        val = redis.get(key)
        if val and val.isdigit():
            val = int(val)
        result[key] = val

    return json.dumps(result)
