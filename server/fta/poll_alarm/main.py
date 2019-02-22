# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
#
# Poll alarm from other system to kafka
# Alarm should be cleaning to a specified standard dict

import importlib
import signal
import sys
import time
import types

from fta import constants, settings
from fta.poll_alarm.process import BasePollAlarm
from fta.poll_alarm.sched import EmptyJobs, schedule
from fta.utils import logging, send_notice

logger = logging.getLogger("poll_alarm")

SHUTDOWN = False


def onsignal(signum, frame):
    """handle quit signal"""
    logger.info('poll_alarm schedule shutdown')
    schedule.clear()

    global SHUTDOWN
    SHUTDOWN = True


def start_schedule():
    schedule.clear()

    # 任意脚本类型，注意脚本必须是绝对路径
    for command, cron in settings.DEFAULT_SCRIPT_CRONTAB:
        schedule.every().cron(cron).run_script(command, name=command)

    # python -m module 类型
    for module_name, cron in settings.DEFAULT_CRONTAB:
        command = "%s -m %s " % (settings.PYTHON, module_name)
        schedule.every().cron(cron).run_script(command, verbose=False, name=module_name)

    # poll_alarm 类型
    for poll_name in settings.POLL_LIST:
        schedule.every(settings.POLL_INTERVAL).minutes.run_func(start_poll_alarm, poll_name, name=poll_name)

    # 启动首次运行, for test
    # schedule.run_all()

    if len(schedule.jobs) == 0:
        raise EmptyJobs

    while schedule.jobs:
        schedule.run_pending()
        time.sleep(1)

    schedule.wait_job_done()


def start_poll_alarm(module_name):
    """start poll process"""
    module = importlib.import_module("project.poll_alarm.%s" % module_name)
    for name in dir(module):
        cls_obj = getattr(module, name)
        if isinstance(cls_obj, (type, types.ClassType)) \
                and issubclass(cls_obj, BasePollAlarm) \
                and cls_obj.__module__.split('.')[-1] == module_name:
            poll_obj = cls_obj()
            poll_obj.start()


def main():
    if len(sys.argv) >= 2:
        start_poll_alarm(sys.argv[1])
        return

    signal.signal(signal.SIGTERM, onsignal)
    signal.signal(signal.SIGINT, onsignal)
    while not SHUTDOWN:
        try:
            start_schedule()
        except EmptyJobs:
            logger.warning('had no jobs, will sleep %s seconds for next loop' % settings.EXCEPTION_RETRY_INTERVAL)
            time.sleep(settings.EXCEPTION_RETRY_INTERVAL)
        except Exception as e:
            logger.exception("%s %s", constants.ERROR_01_POLL, e)
            send_notice.exception(e)
            logger.info('exception occur, will retrying in %s(s).' % settings.EXCEPTION_RETRY_INTERVAL)
            time.sleep(settings.EXCEPTION_RETRY_INTERVAL)


if __name__ == "__main__":
    main()
