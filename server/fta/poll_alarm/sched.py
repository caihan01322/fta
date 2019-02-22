# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import multiprocessing
import os
import shlex
import signal
import subprocess
import time

import psutil
from crontab import CronTab
from schedule import Job as _Job
from schedule import Scheduler as _Scheduler

from fta import constants
from fta.utils import logging

logger = logging.getLogger("poll_alarm")


class Scheduler(_Scheduler):

    def __init__(self):
        super(Scheduler, self).__init__()
        self.running_process = set()

    def run_pending(self):
        super(Scheduler, self).run_pending()
        self.clean_process()

    def clean_process(self):
        dead_process = set()

        for process in self.running_process:
            if process.is_alive():
                ps = psutil.Process(process.pid)
                running_time = time.time() - ps.create_time()
                if running_time < constants.JOB_EXCEUTE_TIMEOUT:
                    continue

                logger.warning("job process %s execute over %.2f(s), more than %s(s), try to force shutdown." % (
                    ps, running_time, constants.JOB_EXCEUTE_TIMEOUT
                ))
                self.force_shtudown([process])
            else:
                dead_process.add(process)
                logger.info('stoped job process %s, pid=%s' % (process, process.pid))

        self.running_process -= dead_process

    def every(self, interval=1):
        job = Job(interval, self)
        self.jobs.append(job)
        return job

    def graceful_shutdown(self, running_process):
        for process in running_process:
            if not process.is_alive():
                continue

            children = psutil.Process(process.pid).children(recursive=True)
            for p in children:
                p.terminate()
                logger.info('graceful shutdown children process %s' % p)
            process.terminate()
            logger.info('graceful shutdown job process %s, pid=%s' % (process, process.pid))

    def force_shtudown(self, running_process):
        for process in running_process:
            if not process.is_alive():
                continue

            children = psutil.Process(process.pid).children(recursive=True)
            for p in children:
                p.kill()
                logger.warning('force shutdown children process %s' % p)
            os.kill(process.pid, signal.SIGKILL)
            logger.warning('force shutdown job process %s, pid=%s' % (process, process.pid))

    def wait_job_done(self, timeout=5):
        logger.info('wait job done')

        self.graceful_shutdown(self.running_process)
        st = time.time()

        while len(self.running_process) > 0:
            if (time.time() - st) > timeout:
                logger.warning('graceful shutdown timeout(%ss), try to force shutdown' % timeout)
                self.force_shtudown(self.running_process)

            self.clean_process()
            time.sleep(1)

        logger.info('all job done')


class Job(_Job):

    def __init__(self, interval, scheduler):
        super(Job, self).__init__(interval)
        self.scheduler = scheduler

    def cron(self, crontab):
        """crontab类型
        """

        # crons for log petty
        self.unit = 'crons'

        try:
            self.cron_entry = CronTab(crontab)
        except Exception as error:
            raise Exception('crontab(%s) parse error: %s' % (crontab, error))

        return self

    def run_script(self, command, *args, **kwargs):
        """运行脚本类型
        """
        job = self.do(script_executor, command, *args, **kwargs)
        logger.info('add job %s' % job)
        return job

    def run_func(self, func, *args, **kwargs):
        """运行函数类型
        """
        job = self.do(func_executor, func, *args, **kwargs)
        logger.info('add job %s' % job)
        return job

    def run(self):
        logger.info('running job %s' % self)

        try:
            ret = self.job_func()
        except Exception as error:
            logger.exception('running job_func error: %s' % error)
            ret = None

        if isinstance(ret, (subprocess.Popen, multiprocessing.Process)):
            logger.info('start job process %s, pid=%s' % (ret, ret.pid))
            self.scheduler.running_process.add(ret)

        # run use local time, do not use utc time
        self.last_run = datetime.datetime.now()
        self._schedule_next_run()
        return ret

    def _schedule_next_run(self):
        """
        Compute the instant when this job should run next.
        """
        if self.unit == 'crons':
            next_delta = self.cron_entry.next(default_utc=False)
            # run use local time, do not use utc time
            self.next_run = datetime.datetime.now() + datetime.timedelta(seconds=next_delta)
        else:
            self._schedule_next_run_period()

    def _schedule_next_run_period(self):
        """
        Compute the instant when this job should run next.
        """
        assert self.unit in ('seconds', 'minutes', 'hours', 'days', 'weeks')
        self.period = datetime.timedelta(**{self.unit: self.interval})

        # fix time offset problem
        if not self.next_run:
            self.next_run = datetime.datetime.now() + self.period
        else:
            self.next_run = self.next_run + self.period

        if self.start_day is not None:
            assert self.unit == 'weeks'
            weekdays = (
                'monday',
                'tuesday',
                'wednesday',
                'thursday',
                'friday',
                'saturday',
                'sunday'
            )
            assert self.start_day in weekdays
            weekday = weekdays.index(self.start_day)
            days_ahead = weekday - self.next_run.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            self.next_run += datetime.timedelta(days_ahead) - self.period
        if self.at_time is not None:
            assert self.unit in ('days', 'hours') or self.start_day is not None
            kwargs = {
                'minute': self.at_time.minute,
                'second': self.at_time.second,
                'microsecond': 0
            }
            if self.unit == 'days' or self.start_day is not None:
                kwargs['hour'] = self.at_time.hour
            self.next_run = self.next_run.replace(**kwargs)
            # If we are running for the first time, make sure we run
            # at the specified time *today* (or *this hour*) as well
            if not self.last_run:
                now = datetime.datetime.now()
                if (self.unit == 'days' and self.at_time > now.time() and self.interval == 1):
                    self.next_run = self.next_run - datetime.timedelta(days=1)
                elif self.unit == 'hours' and self.at_time.minute > now.minute:
                    self.next_run = self.next_run - datetime.timedelta(hours=1)
        if self.start_day is not None and self.at_time is not None:
            # Let's see if we will still make that time we specified today
            if (self.next_run - datetime.datetime.now()).days >= 7:
                self.next_run -= self.period


schedule = Scheduler()


class EmptyJobs(Exception):
    pass


class Process(multiprocessing.Process):

    def run(self):
        try:
            super(Process, self).run()
        except Exception as error:
            logger.exception('run %s(%s, %s) process error: %s' % (
                self._target.__name__, self._args, self._kwargs, error))


def func_executor(func, *args, **kwargs):
    """函数执行
    """
    name = kwargs.pop('name', None)
    process = Process(target=func, name=name, args=args, kwargs=kwargs)
    process.daemon = True

    process.start()

    return process


def script_executor(command, verbose=True, name=None):
    """命令行执行
    """

    def script_wrapper(command, verbose):
        args = shlex.split(command)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.info('start script process %s, pid=%s' % (process, process.pid))

        # 注意: script stderr必须换行才会输出, stdout只有完成才输出
        for line in iter(process.stdout.readline, ''):
            if verbose:
                logger.info(line.strip())

        process.terminate()
        process.wait()
        logger.info('stoped script process %s, pid=%s' % (process, process.pid))

    return func_executor(script_wrapper, command, verbose, name=name)
