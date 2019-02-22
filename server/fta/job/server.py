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

from flask import Flask, request
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer

from fta import settings
from fta.storage.queue import MessageQueue
from fta.utils import lock, logging, timeout
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.context import Context
from fta.utils.continuation import WaitCallback
from fta.utils.i18n import _, i18n
from fta.www.utils import response

app = Flask(__name__)
# For most server frameworks, setting debug to True can result in a memory leak
app.debug = False

logger = logging.getLogger("job")

SOLUTION_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_SOLUTION)


@app.route("/job/<instance_id>/<node_idx>/", methods=["POST"])
@response.api
@response.log
def job(instance_id, node_idx):
    """
    Job Server
    :param instance_id: alarm_instance's id
    :param node_idx: alarm_instance's solution's node's id
    """

    # get alarm_instance
    alarm_instance = get_alarm_instance(instance_id=instance_id)
    i18n.set_biz(alarm_instance['cc_biz_id'])

    # loads job_info from post data
    job_info = json.loads(request.get_data())

    logger.info(
        "$%s &%s Job call %s.solution.%s(%s) times(%s)",
        alarm_instance["id"], node_idx,
        job_info["module"], job_info["function"],
        job_info["kwargs"], job_info["run_times"])

    try:
        if timeout.get_timeout_time(alarm_instance) <= 0:
            raise timeout.TimeoutError

        # assert alarm_instance run times haven't be updated
        if Context(instance_id).RUN_TIMES != int(job_info["run_times"]):
            run_times_info = "RUN_TIMES: %s/%s" % (Context(instance_id).RUN_TIMES, job_info["run_times"])
            raise WaitCallback(run_times_info)

        # import node's call function
        module = importlib.import_module(job_info["module"])
        solution = module.Solution(
            alarm_instance, node_idx, job_info["run_times"])
        func = getattr(solution, job_info["function"])

        # call func
        func(**job_info["kwargs"])

        # assert alarm_instance run times haven't be updated
        if int(Context(instance_id).RUN_TIMES) != int(job_info["run_times"]):
            run_times_info = "RUN_TIMES: %s/%s" % (Context(instance_id).RUN_TIMES, job_info["run_times"])
            raise WaitCallback(run_times_info)

        if not solution.is_finished():
            raise WaitCallback("wait_callback")
    except WaitCallback as e:
        # current node is not finished. Wait callback and continue
        logger.info("$%s &%s Job end without finished: %s", alarm_instance["id"], node_idx, e)
        return ""
    except timeout.TimeoutError:
        # create timeout instance_info
        instance_info = "::".join([alarm_instance["event_id"], node_idx, "failure"])
    except Exception as e:
        logger.exception(
            "$%s &%s Job error: %s", alarm_instance["id"], node_idx, e)
        # try to set failure status
        try:
            solution.set_finished(
                "failure", _("Exception error: %(error)s", error=e), failure_type="framework_code_failure",
            )
        except BaseException:
            pass
        # create failure instance_info
        instance_info = "::".join([alarm_instance["event_id"], node_idx, "failure"])
    else:
        # create instance_info by job result
        instance_info = "::".join([
            alarm_instance["event_id"], node_idx, solution.result])

    # if retry by SINGLE_NODE_MODE, don't put back to queue
    if Context(instance_id).SINGLE_NODE_MODE:
        try:
            lock.lock_alarm_instance(alarm_instance["event_id"], ["retrying"], instance_info.split("::")[2])
        except Exception as e:
            logger.error("$%s &%s SINGLE_NODE_MODE error: %s", alarm_instance["id"], node_idx, e)
        return ""

    logger.info("$%s &%s Job finish into SolutionQueue: %s", alarm_instance["id"], node_idx, instance_info)

    # put back to solution queue
    SOLUTION_QUEUE.put(str(instance_info), alarm_instance["priority"])


if __name__ == "__main__":
    p = Pool(30)  # at most 30 greenlet
    http = WSGIServer(('0.0.0.0', settings.JOBSERVER_PORT), app, spawn=p)
    http.serve_forever()
