# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

import signal
import time

import gevent
from gevent import monkey

from fta import settings  # noqa
from fta.job.process import Job  # noqa
from fta.utils import logging  # noqa
from fta.utils import send_notice  # noqa

monkey.patch_socket()

logger = logging.getLogger("job")

SHUTDOWN = False


def onsignal(signum, frame):
    """handle quit signal"""
    logger.info("job shutdown")
    global SHUTDOWN
    SHUTDOWN = True


def run_job():
    try:
        job = Job()
        job.start()
    except Exception as e:
        logger.exception(e)
        raise


def main():
    # register signal for process QUIT
    signal.signal(signal.SIGTERM, onsignal)
    signal.signal(signal.SIGINT, onsignal)
    gevent.signal(signal.SIGQUIT, gevent.kill)
    running = []
    while len(running) or not SHUTDOWN:
        success_num = 0
        for thread in running:
            if thread.ready():
                if thread.successful():
                    success_num += 1
                else:
                    logger.error(thread.exception)
                running.remove(thread)
        if not success_num:
            logger.info('exception occur, will retrying in %s(s).' % settings.EXCEPTION_RETRY_INTERVAL)
            time.sleep(settings.EXCEPTION_RETRY_INTERVAL)
        if SHUTDOWN:
            logger.info("Running Job SHUTDOWN %s", len(running))
            gevent.sleep(2)
            continue
        if len(running) >= settings.JOBSERVER_MAX:
            logger.info("Running Job MAX %s", len(running))
            gevent.sleep(2)
            continue
        try:
            thread = gevent.spawn(run_job)
            running.append(thread)
            thread.join(timeout=settings.JOBSERVER_TIMEOUT)
        except Exception as e:
            running.remove(thread)
            logger.exception(e)
            send_notice.exception(e)


if __name__ == "__main__":
    main()
