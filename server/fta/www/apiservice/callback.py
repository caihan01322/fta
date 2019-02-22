# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from flask import request
from fta import constants
from fta.solution.base import BaseSolution
from fta.solution.fsm import FSM
from fta.utils import instance_log, lock, logging
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.context import Context, ContextAcquireException
from fta.utils.continuation import get_callback_info, put_result_to_job_queue
from fta.utils.i18n import _, lazy_gettext
from fta.www.apiservice import fta_api_page as app
from fta.www.utils import response

logger = logging.getLogger("apiserver")


@app.route("/callback/<instance_uniqid>/", methods=["POST"])
@response.log
def component_callback(instance_uniqid):
    try:
        job_info = get_callback_info(
            instance_uniqid,
            result=request.get_json(silent=True) or request.form,
        )
        put_result_to_job_queue(id_=instance_uniqid, **job_info)
    except Exception as e:
        error_message = "esb_id %s: callback error: %s" % (instance_uniqid, e)
        raise Exception(error_message)
    return "OK"


@app.route("/callback_null/<instance_uniqid>/", methods=["POST"])
@response.log
def component_callback_null(instance_uniqid):
    """fake callback"""
    return "OK"


@app.route("/callback/<instance_id>/<node_idx>/", methods=["POST"])
@response.api
@response.log
def retry_solution(instance_id, node_idx):
    alarm_instance = get_alarm_instance(instance_id=int(instance_id))

    if alarm_instance["status"] not in constants.INSTANCE_END_STATUS:
        raise Exception(_("Current flow is in execution and cannot be retried"))

    context = Context(instance_id)
    # context.RUN_TIMES = context.RUN_TIMES or 0  # for test
    RUN_TIMES = context._load_key("RUN_TIMES") or 0  # noqa
    try:
        context._acquire("RUN_TIMES", RUN_TIMES, RUN_TIMES + 1)
    except ContextAcquireException:
        raise Exception(_("Current flow is in execution and cannot be retried"))

    try:
        lock.lock_alarm_instance(
            alarm_instance["event_id"], alarm_instance["status"], "retrying")
    except lock.LockError:
        raise Exception(_("Current flow is in execution and cannot be retried"))

    # get module
    solution = BaseSolution.get_solution(alarm_instance, node_idx)
    module = "manager.solution.%s" % solution["solution_type"]

    # init context
    context.SINGLE_NODE_MODE = "SINGLE_NODE_MODE" in request.form
    fsm_context = FSM.get_context(instance_id, context.RUN_TIMES)
    fsm_context.wait_node = [str(node_idx)]

    # log retry begin
    instance_log.update_alarm_instance_comment(
        alarm_instance_id=instance_id, cover=True,
        comment=_("Start to retry from node #%(node_idx)s[%(title)s]",
                  node_idx=node_idx, title=lazy_gettext(solution['title'])))

    put_result_to_job_queue(
        instance_id, node_idx, context.RUN_TIMES, module, "run")
