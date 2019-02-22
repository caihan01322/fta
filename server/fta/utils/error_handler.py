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

import arrow

from fta.storage.mysql import session
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import logging, send_message
from fta.utils.i18n import _

logger = logging.getLogger("utils")


def exception(alarm_instance):
    if 'event_id' not in alarm_instance:
        return
    session.query(FtaSolutionsAppAlarminstance)\
        .filter_by(event_id=alarm_instance['event_id'])\
        .update({
            "status": "failure",
            "failure_type": "framework_code_failure",
            "comment": _("Execution error occurred"),
            "end_time": arrow.utcnow().naive})
    alarm_instance['status'] = "failure"
    alarm_instance['failure_type'] = "framework_code_failure"
    send_message.notify_info(alarm_instance)


def solution_timeout(alarm_instance):
    try:
        solution = json.loads(alarm_instance['snap_solution'] or '{}')
        module = importlib.import_module(
            "manager.solution.%s" % solution['solution_type'])
        assert module.Solution.timeout
    except BaseException:
        raise ImportError
    module.Solution(alarm_instance, 0).timeout()


def default_timeout(alarm_instance):
    if alarm_instance['status'] in ['received', 'sleep', 'converging']:
        status = _("Convergence")
    elif alarm_instance['status'] in ['recovering', 'converged', 'waiting']:
        status = _("Processing")
    else:
        status = _("Auto-recovery")

    session.query(FtaSolutionsAppAlarminstance)\
        .filter_by(event_id=alarm_instance['event_id'])\
        .update({
            "status": "failure",
            "failure_type": "timeout",
            "comment": _("Timeout in %(status)s", status=status),
            "end_time": arrow.utcnow().naive})

    alarm_instance['status'] = "failure"
    alarm_instance['failure_type'] = "time"
    send_message.notify_info(alarm_instance)


def timeout(alarm_instance):
    try:
        return solution_timeout(alarm_instance)
    except ImportError:
        logger.info("$%s timeout by default", alarm_instance["id"])
    except Exception as e:
        logger.exception(
            "$%s timeout by solution error: %s", alarm_instance["id"], e)
    default_timeout(alarm_instance)
