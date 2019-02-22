# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import arrow
import requests

from fta import constants, settings
from fta.polling.task import parallel
from fta.storage.queue import MessageQueue
from fta.utils import extended_json, lock, logging, scheduler

logger = logging.getLogger('polling')

POLLING_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_POLLING)


class Polling(object):

    def __init__(self):
        self.job_list = []
        self.queue = POLLING_QUEUE

    @staticmethod
    def check_detail_seconds(task_info):
        """check time error"""
        exe_time = arrow.get(task_info["time"]).replace(tzinfo='local')
        delta_seconds = (arrow.utcnow() - exe_time).total_seconds()
        if abs(delta_seconds) > 60:
            logger.error(u'scheduler job miss %s seconds: %s', delta_seconds, task_info)

    def pull_task(self, task_info_list=()):
        """
        pull task_info from queue or args
        :param task_info: dict as
            {
                "id": "task_id",  # task with same id will only exec once
                "module": "module_name",  # function's module's name or path
                "function": "function_name",  # which function to be exec
                "args": (),  # args' list
                "kwargs": {},  # kwargs' dict
                "cron": "",  # like "* * * * *" or ""
                "time": "2015-01-01 11:11:11",  # when to exec
                "timeout": "10"  # seconds
            }
        """

        if task_info_list:
            self.task_info_list = list(task_info_list)
            return

        self.task_info_list = []

        for i in range(100):
            job = self.queue.take(timeout=1)

            # if not job, raise to end process
            if not job:
                if not self.task_info_list:
                    raise lock.PassEmpty
                break

            self.job_list.append(job)
            task_info = extended_json.loads(job.body)

            # if runned this job, pass
            if not lock.redis_lock("polling_%s" % task_info['id']):
                logger.info("pass scheduler %s", task_info['id'])
                continue

            logger.info("Polling get task_info: %s", task_info)

            self.check_detail_seconds(task_info)
            self.task_info_list.append(task_info)

        logger.info("Polling task_info length: %s", len(self.task_info_list))

    def handle_task(self):
        """run task as subprocess"""

        # logging
        for task_info in self.task_info_list:
            logger.info(
                "call_poll %s.%s(*%s, poll(%s)) timeout=%s",
                task_info['module'],
                task_info['function'],
                task_info['args'],
                task_info['kwargs'],
                task_info['timeout'])

        # run_parallel get polling result
        kwargs_list = [i['kwargs'] for i in self.task_info_list]
        logger.info("scheduler parallel: %s", kwargs_list)
        self.result_list = parallel(requests.post, kwargs_list)

    def push_task(self):
        self._push_to_scheduler()
        # self._push_back_to_queue  # don't use because can't delete cron job

    def _push_to_scheduler(self):
        """push to scheduler queue for running callback function"""
        logger.info("Polling task_info_list: %s result_list: %s", self.task_info_list, self.result_list)
        for task_info, result in zip(self.task_info_list, self.result_list):
            scheduler.run(
                id_=task_info['id'],
                module=task_info['module'],
                function=task_info['function'],
                args=task_info['args'],
                kwargs={"result": result.text},
                time=arrow.utcnow().format(constants.STD_ARROW_FORMAT),
                timeout=task_info['timeout'])

    def _push_back_to_queue(self):
        """push cron job back to queue"""
        for task_info in self.task_info_list:
            if task_info.get('cron'):
                scheduler.poll(
                    module=task_info['module'],
                    function=task_info['function'],
                    args=task_info['args'],
                    kwargs=task_info['kwargs'],
                    cron=task_info['cron'],
                    timeout=task_info['timeout'])

    def start(self):
        try:
            self.pull_task()
            self.handle_task()
            self.push_task()
        except lock.LockError as e:
            logger.info(e)
        except lock.PassEmpty:
            pass
        finally:
            for job in self.job_list:
                job.delete()
