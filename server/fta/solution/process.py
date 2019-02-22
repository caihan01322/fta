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

from fta import constants, settings
from fta.solution import CONTEXT
from fta.solution.base import BaseSolution
from fta.solution.fsm import FSM
from fta.storage.mysql import session
from fta.storage.queue import MessageQueue
from fta.storage.tables import FtaSolutionsAppAlarminstance
from fta.utils import error_handler, get_random_id, instance_log, lock, logging, send_message, send_notice, timeout
from fta.utils.alarm_instance import get_alarm_instance
from fta.utils.context import Context
from fta.utils.continuation import WaitCallback
from fta.utils.i18n import _, lazy_gettext
from manager.define.solution import SolutionManager

logger = logging.getLogger('solution')

SOLUTION_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_SOLUTION)
JOB_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_JOB)


class Solution(object):

    def __init__(self):
        self.job = None
        self.alarm_instance = {}
        self.solution = {}
        self.node_status = []
        self.result_list = []

        # 收敛后的结果状态
        self.converged_status = 'converged'

    def pull_alarm(self, instance_info=None, alarm_instance={}):
        """
        :param instance_info: event_id or event_id::node_idx::solution.result
        :param alarm_instance: alarm_instance dict
        """

        # init instance_info
        if not instance_info:
            self.job = SOLUTION_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)
            if not self.job:
                raise lock.PassEmpty
            instance_info = self.job.body
        self.instance_info = instance_info
        logger.info("solution get instance_info: %s", instance_info)

        # init self.alarm_instance
        if not alarm_instance:
            event_id = instance_info.split("::")[0]
            alarm_instance = get_alarm_instance(event_id=event_id)
        self.alarm_instance = alarm_instance

        CONTEXT.set("id", self.alarm_instance["id"])

        # first time run solution process
        if self._is_first_node():
            self.converged_status = lock.lock_alarm_instance(
                self.alarm_instance['event_id'], ['converged', 'waiting'], 'recovering'
            )
            # send_message begin
            send_message.notify_info(self.alarm_instance)

        # lock instance node
        lock.lock_alarm_instance_node(*instance_info.split("::")[:2])

        # assert instance status
        self.assert_status()

        self._init_context(instance_info)

    def _is_first_node(self):
        return not self.instance_info.split("::")[1:]

    def _init_context(self, instance_info):
        logger.info(
            "$%s solution event_id: %s",
            self.alarm_instance["id"],
            self.alarm_instance['event_id'])

        self.node_status = instance_info.split("::")[1:]
        self.solution = json.loads(self.alarm_instance['snap_solution'] or '{}')
        self.graph_json = BaseSolution.convert_solution2graph(self.solution)
        logger.info(
            "$%s graph_json %s", self.alarm_instance["id"], self.graph_json)

        # init run times
        self.context = Context(self.alarm_instance["id"])
        self.context.RUN_TIMES = self.context.RUN_TIMES or 0

        # only set timeout in first run
        if not self.context.RUN_TIMES:
            timeout.set_timeout(timeout.get_timeout_time(self.alarm_instance))

    def assert_status(self):
        """assert alarm_instance's status is not end"""
        status = session.query(FtaSolutionsAppAlarminstance).filter_by(id=self.alarm_instance["id"]).one().status
        # almost_success in INSTANCE_END_STATUS, but infact may still running
        try:
            assert status in ["almost_success"] or status not in constants.INSTANCE_END_STATUS
        except BaseException:
            raise lock.LockError("assert status error: %s" % status)

    def handle_alarm(self):
        logger.info("$%s run solution %s", self.alarm_instance["id"], self.solution)

        # first time logger begin info
        if self._is_first_node():
            instance_log.update_alarm_instance_comment(
                alarm_instance_id=self.alarm_instance["id"],
                comment=_("Start processing solution [%(solution)s]", solution=lazy_gettext(self.solution["title"])),
                cover=False)

        # wait for approve by biz_verifier, call approve solution
        if self.converged_status == "waiting":
            JOB_QUEUE.put(json.dumps(self.get_job_info(-1)))
            raise WaitCallback(json.dumps([-1]))

        # approve deny
        if self.node_status and int(self.node_status[0]) == -1 and self.node_status[1] != "success":
            return

        # get wait/run node by FSM
        fsm = FSM(self.alarm_instance["id"], self.graph_json,
                  self.context.RUN_TIMES)

        if self.node_status and int(self.node_status[0]) >= 0:
            fsm.receive(*self.node_status)

        wait_node, run_node = fsm.input_status()

        # put run node to JOB QUEUE
        for node_idx in run_node:
            logger.info("$%s put node into job queue: %s", self.alarm_instance["id"], node_idx)
            JOB_QUEUE.put(json.dumps(self.get_job_info(node_idx)), self.alarm_instance["priority"])

        # waitting wait node
        if wait_node:
            # Solution still not finished
            raise WaitCallback(json.dumps(wait_node))

        # get solution finished status
        self.result_list = fsm.result_list()

    def get_job_info(self, node_idx):
        if int(node_idx) >= 0:
            solution_id = str(self.graph_json[int(node_idx)][1])
            solution = SolutionManager().raw_solution_dict[solution_id]
            solution_type = solution["solution_type"]
        elif int(node_idx) == -1:
            solution_type = "waiting"
        return {
            "id": get_random_id(),
            "instance_id": self.alarm_instance["id"],
            "node_idx": node_idx,
            "run_times": self.context.RUN_TIMES,
            "module": "manager.solution.%s" % solution_type,
            "function": "run",
            "kwargs": {},
        }

    @property
    def status(self):
        if self.node_status and int(self.node_status[0]) == -1:
            return self.node_status[1]
        # almost_success > failue > skipped > others > success
        if Context(self.alarm_instance["id"]).is_almost_success:
            return "almost_success"
        if "failure" in self.result_list:
            return "failure"
        if "skipped" in self.result_list:
            return "skipped"
        for result in self.result_list:
            if result != "success":
                return result
        assert "success" in self.result_list
        return "success"

    @property
    def comment(self):
        if self.node_status and int(self.node_status[0]) == -1:
            return self.get_node_solution_comment(-1)
        elif self.solution["solution_type"] not in ["diy", "graph"]:
            return self.get_node_solution_comment(0)
        else:
            return _("Execute combination solution[%(title)s]%(status)s",
                     title=lazy_gettext(self.solution["title"]),
                     status=constants.INSTANCE_STATUS_DESCRIPTION.get(self.status, self.status))

    def get_node_solution_comment(self, node_idx):
        solution_context_id = BaseSolution.get_context_id(self.alarm_instance["id"], node_idx)
        return Context(solution_context_id).comment

    def push_alarm(self):
        # update status
        try:
            lock.lock_alarm_instance(
                self.alarm_instance["event_id"], ["recovering", "almost_success", "retrying"], self.status)
        except lock.LockError:
            raise Exception("End Lock Failure")

        # update comment & end_time
        session.query(
            FtaSolutionsAppAlarminstance
        ).filter_by(event_id=self.alarm_instance['event_id']).update({
            "comment": self.comment,
            "end_time": arrow.utcnow().naive
        })

        # send_message end (reload alarm_instance from db)
        alarm_instance = get_alarm_instance(self.alarm_instance["id"])
        send_message.notify_info(alarm_instance)

        logger.info("$%s solution finished event_id: %s", self.alarm_instance["id"], self.alarm_instance['event_id'])

    def start(self):
        try:
            self.pull_alarm()
            self.handle_alarm()
            self.push_alarm()
        except WaitCallback as e:
            logger.info("$%s wait_callback %s", self.alarm_instance["id"], e)
        except timeout.TimeoutError:
            error_handler.timeout(self.alarm_instance)
        except lock.LockError as e:
            logger.info(e)
        except lock.PassEmpty:
            pass
        except Exception as e:
            error_message = u"$%s frame_error %s" % (self.alarm_instance.get("id"), e)
            send_notice.exception(error_message)
            logger.exception(error_message)
            error_handler.exception(self.alarm_instance)
            raise
        finally:
            if self.job:
                self.job.delete()
            timeout.del_timeout()
