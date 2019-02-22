# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2018 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa

WEBSERVER_PORT = 8081
APISERVER_PORT = 8082
CISERVER_PORT = 8083
JOBSERVER_PORT = 8090
JOBSERVER_MAX = 40
JOBSERVER_TIMEOUT = 60

RECONNECT_INTERVAL = 60  # 当连接redis或beanstalkd失败之后多少秒内不尝试重连
EXCEPTION_RETRY_INTERVAL = 60  # 进程异常重试时间，和beanstalkd阻塞时间保持一致
QUEUE_WAIT_TIMEOUT = 5  # 队列等待超时时间

# beanstalk tube name
QUEUE_CONVERGE = 'FTA_ALARMS_TO_CONVERGE'
QUEUE_JOB = 'FTA_ALARMS_TO_JOB'
QUEUE_SOLUTION = 'FTA_ALARMS_TO_SOLUTION_NEW'  # 叫 NEW 是因为升级过一次
QUEUE_COLLECT = 'FTA_ALARMS_TO_COLLECT'
QUEUE_SCHEDULER = 'FTA_ALARMS_TO_SCHEDULER'
QUEUE_POLLING = 'FTA_ALARMS_TO_POLLING'

# 告警匹配队列，poll_alarm和match_alarm解耦后新队列
QUEUE_MATCH = 'FTA_ALARMS_TO_MATCH'

# beanstalk block args
BLOCK_CHECK_INTERVAL = 60
BLOCK_TIME_THRESHOLD = 5  # More than this num jobs in queue, means blocked

FTA_LOGFILE_MAXSIZE = 1024 * 1024 * 1024 * 1  # 1GB
FTA_LOGFILE_MAXSIZE_GLOBAL = 1024 * 1024 * 1024 * 3  # 3GB
FTA_PROCESS_CHECK_TIME = 60 * 60 * 4

# add kafka client connect log
LOGGER_KAFKA_CLIENT = {
    "level": "WARNING",
    "handlers": ["console", "file", "redis"],
}

# LOGGING
LOG_LEVEL = "DEBUG"
LOGGER_CONF = None
LOG_PATH = "logs"

# 默认时区
DEFAULT_TIMEZONE = 'Asia/Shanghai'
# 默认语言
DEFAULT_LOCALE = 'zh_Hans_CN'


def get_log_config(level=None, logger_default=None, log_path=None):
    import os

    logger_default = logger_default or {
        "level": level or LOG_LEVEL,
        "handlers": ["console", "file", "redis"],
    }
    log_path = log_path or LOG_PATH
    if os.path.isdir(log_path):
        log_path = os.path.join(log_path, "fta.log")

    return LOGGER_CONF or {
        "version": 1,
        "loggers": {
            "root": logger_default,
            "fta": logger_default,
            "poll_alarm": logger_default,
            "match_alarm": logger_default,
            "collect": logger_default,
            "converge": logger_default,
            "solution": logger_default,
            "job": logger_default,
            "ja": logger_default,
            "qos": logger_default,
            "scheduler": logger_default,
            "polling": logger_default,
            "webserver": logger_default,
            "apiserver": logger_default,
            "utils": logger_default,
            "advice": logger_default,
            "event": logger_default,
            "watchdog": logger_default,
            "test": logger_default,
            "component": logger_default,
            "contrib": logger_default,
            "project": logger_default,
            "manager": logger_default,
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "standard",
            },
            "file": {
                "class": "logging.handlers.WatchedFileHandler",
                "level": "DEBUG",
                "formatter": "standard",
                "filename": log_path,
            },
            "redis": {
                "class": "fta.logging.handlers.RedisHandler",
                "level": "DEBUG",
            }
        },
        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s %(levelname)-8s %(process)-8d"
                    "%(name)-15s %(filename)20s[%(lineno)03d] %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        }
    }


try:
    from project import settings
    locals().update(settings.__dict__)
except Exception as e:
    print u'!!!!! WARNING: CAN NOT FIND USER SETTINGS !!!!!'
    import traceback
    print traceback.format_exc()
    import sys
    sys.exit(0)

LOGGER_CONF = get_log_config()  # allow inject LOG_LEVEL
