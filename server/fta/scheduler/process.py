# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

from multiprocessing import Process

import arrow

from fta import settings
from fta.scheduler.task import run
from fta.storage.queue import MessageQueue
from fta.utils import extended_json, lock, logging, scheduler

logger = logging.getLogger('scheduler')

SCHEDULER_QUEUE = MessageQueue("beanstalkd", topic=settings.QUEUE_SCHEDULER)


class Scheduler(object):

    def __init__(self):
        self.job = None

    @staticmethod
    def check_detail_seconds(task_info):
        """check time error"""
        exe_time = arrow.get(task_info["time"])
        delta_seconds = (arrow.utcnow() - exe_time).total_seconds()
        if abs(delta_seconds) > 60:
            logger.error(u'scheduler job miss %s seconds: %s', delta_seconds, task_info)

    def pull_task(self, task_info=None):
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
        if not task_info:
            self.job = SCHEDULER_QUEUE.take(timeout=settings.QUEUE_WAIT_TIMEOUT)

            # if not job, raise to end process
            if not self.job:
                raise lock.PassEmpty

            task_info = extended_json.loads(self.job.body)

            # if runned this job, raise to end process
            if not lock.redis_lock("scheduler_%s" % task_info['id']):
                raise lock.LockError("pass scheduler %s" % task_info['id'])

            self.check_detail_seconds(task_info)
        self.task_info = task_info

    def handle_task(self):
        """run task as subprocess"""

        logger.info(
            "call %s.%s(*%s, **%s) timeout=%s",
            self.task_info['module'],
            self.task_info['function'],
            self.task_info['args'],
            self.task_info['kwargs'],
            self.task_info['timeout'])

        # run real function
        process = Process(
            target=run,
            args=(
                self.task_info['module'],
                self.task_info['function'],
                self.task_info['timeout']),
            kwargs={
                'args': self.task_info['args'],
                'kwargs': self.task_info['kwargs']}
        )
        process.start()

    def push_task(self):
        """push cron job back to queue"""
        if self.task_info.get('cron'):
            scheduler.run(
                module=self.task_info['module'],
                function=self.task_info['function'],
                args=self.task_info['args'],
                kwargs=self.task_info['kwargs'],
                cron=self.task_info['cron'],
                timeout=self.task_info['timeout'])

    def start(self):
        try:
            self.pull_task()
            self.handle_task()
            # self.push_task()  # don't use because can't delete cron job
        except lock.LockError as e:
            logger.info(e)
        except lock.PassEmpty:
            pass
        finally:
            if self.job:
                self.job.delete()
