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

import arrow

from fta import settings
from fta.logging.process import LogProcess, clean_log_by_size, move_log_by_day, move_log_by_size
from fta.storage.cache import Cache
from fta.utils import hooks, send_notice

hook = hooks.HookManager("logging")
LogProcess = hook.get_by_argv("LogProcess", LogProcess)

IS_STOPING = False


def onsignal(signum, frame):
    """handle quit signal"""
    global IS_STOPING
    IS_STOPING = True


redis_client = Cache("log")

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, onsignal)
    signal.signal(signal.SIGINT, onsignal)
    if not hasattr(redis_client, "redis"):
        send_notice.error("redis error for log")
    day = arrow.now().day
    minute = arrow.now().minute
    while not IS_STOPING:
        try:
            log_process = LogProcess()
            log_process.start(100)
            if log_process.record_list:
                hook.batch_push_log(log_process.record_list)

            # split log file every day
            if day != arrow.now().day:
                move_log_by_day()
            day = arrow.now().day

            # check and split log file by size every 5 minutes
            if minute != arrow.now().minute and arrow.now().minute % 5 == 0:
                move_log_by_size()
                # clean by global size
                clean_log_by_size()
            minute = arrow.now().minute

        except Exception as e:
            send_notice.exception(e)
            # logger module use print in case cycle error
            print('exception occur, will retrying in %s(s).' % settings.EXCEPTION_RETRY_INTERVAL)
            time.sleep(settings.EXCEPTION_RETRY_INTERVAL)
