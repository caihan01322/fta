# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
#
# Poll task from message queue for polling
import signal
import time

import gevent
from fta import settings
from fta.polling.process import Polling
from fta.utils import logging, send_notice

logger = logging.getLogger('polling')

SHUTDOWN = False


def onsignal(signum, frame):
    """handle quit signal"""
    logger.info('polling shutdown')
    global SHUTDOWN
    SHUTDOWN = True


def main():
    signal.signal(signal.SIGTERM, onsignal)
    signal.signal(signal.SIGINT, onsignal)
    gevent.signal(signal.SIGQUIT, gevent.kill)
    while not SHUTDOWN:
        try:
            polling = Polling()
            polling.start()
            time.sleep(20)
        except Exception as e:
            logger.exception(e)
            send_notice.exception(e)
            logger.info('exception occur, will retrying in %s(s).' % settings.EXCEPTION_RETRY_INTERVAL)
            time.sleep(settings.EXCEPTION_RETRY_INTERVAL)


if __name__ == '__main__':
    main()
