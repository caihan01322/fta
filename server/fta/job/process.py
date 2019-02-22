# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import json
import time

import requests

from fta import constants, settings
from fta.storage.queue import MessageQueue
from fta.utils import alarm_instance, error_handler, lock, logging, send_notice

logger = logging.getLogger("job")

JOB_QUEUE = MessageQueue("beanstalkd", settings.QUEUE_JOB)


class Job(object):

    def pull_job(self, job_info={}):
        """
        pull job_info from queue or args
        :param job_info: dict as
            {
                "id": "job_id",  # job with same id will only exec once
                "instance_id": "alarm_instance_id",
                "node_idx": "node_idx",  # solution_conf's graph node idx
                "module": "module_name",  # function's module's name or path
                "function": "function_name",  # which function to be exec
                "kwargs": {},  # kwargs' dict
            }
        """
        if not job_info:
            self.job = JOB_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)

            # if not job, raise to end process
            if not self.job:
                raise lock.PassEmpty

            job_info = json.loads(self.job.body)

        logger.info("Job get job_info: %s", job_info)
        self.job_info = job_info
        self.verifier_by_alarm_instance()

    def verifier_by_alarm_instance(self):
        self.alarm_instance = alarm_instance.get_alarm_instance(instance_id=self.job_info["instance_id"])

        # assert alarm_instance's status
        if self.alarm_instance["status"] in constants.INSTANCE_FAILURE_STATUS:
            logger.info("$%s Job stop by status %s", self.alarm_instance["id"], self.alarm_instance["status"])
            raise lock.LockError

        # if runned this job, raise to end process
        lock.lock_alarm_instance_node(self.alarm_instance["event_id"], self.job_info["node_idx"], self.job_info["id"])

    @property
    def job_url(self):
        return "%s:%s/job/%s/%s/" % (
            getattr(settings, "JOBSERVER_URL", "http://127.0.0.1"),
            settings.JOBSERVER_PORT,
            self.job_info["instance_id"],
            self.job_info["node_idx"])

    def run_job(self):
        logger.info("$%s Job call %s %s", self.job_info["instance_id"], self.job_url, self.job_info)
        try:
            r = requests.post(self.job_url, json.dumps(self.job_info), timeout=60)
        except requests.ConnectionError:
            time.sleep(15)
            r = requests.post(self.job_url, json.dumps(self.job_info), timeout=60)
        logger.info("$%s Job called %s %s %s", self.job_info["instance_id"], self.job_url, self.job_info, r.text)
        if not r.json()["result"]:
            raise Exception(r.json()["message"])

    def push_job(self):
        pass

    def start(self):
        try:
            self.pull_job()
            self.run_job()
            self.push_job()
        except lock.PassEmpty:
            pass
        except lock.LockError as e:
            logger.info(e)
        except Exception as e:
            error_message = u"$%s frame_error %s" % (self.job_info["instance_id"], e)
            send_notice.exception(error_message)
            logger.exception(error_message)
            error_handler.exception(self.alarm_instance)
        finally:
            if self.job:
                self.job.delete()
